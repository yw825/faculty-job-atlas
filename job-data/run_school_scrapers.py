"""
Runs the per-school scrapers in bulk.

Run from job-data/:
    python3 run_school_scrapers.py US --stage postings
    python3 run_school_scrapers.py US --stage postings --verdicts ok
    python3 run_school_scrapers.py US --stage info
    python3 run_school_scrapers.py US --stage postings --redo   # ignore checkpoints

Writes/updates:
    run_log_<country>_<stage>.csv   one row per school: status, count, error

The scripts are imported and their run function called IN THIS PROCESS
rather than shelled out one at a time. Starting a fresh interpreter and a
fresh browser per school would dominate the runtime at this scale; sharing
one browser across all of them is the difference between hours and most of
a day.

Two things this has to survive, both learned from the non-US run:

  * A single school can hang forever on a socket a library never times out.
    Each school therefore runs under a SIGALRM wall-clock limit and is
    recorded as a timeout, rather than stalling the remaining hundreds.

  * A browser can die mid-run (a page crashes it, or the OS reaps it).
    After any failure the shared browser is dropped so the next school
    starts a fresh one, instead of every subsequent school inheriting the
    same broken handle and the whole run failing from that point on.

Resumable: a school whose checkpoint already says 'complete' is skipped
unless --redo is passed, so an interrupted run picks up where it stopped.
"""
import argparse
import csv
import importlib.util
import os
import signal
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib
import job_info_lib as jinfo

MASTER = os.path.join(HERE, 'schools_master.csv')
POSTS_CODE = os.path.join(HERE, 'school_job_posts_code')
INFO_CODE = os.path.join(HERE, 'school_job_info_code')
VERIFY_FMT = os.path.join(HERE, 'careers_link_verification_{country}.csv')


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def checkpoint_status(path):
    try:
        return lib.load_checkpoint(path).get('status', '')
    except Exception:
        return ''


# A school that returns nothing is retried before that zero is believed.
# Sites serve a short error page under load and then the real one moments
# later -- Cal State Dominguez Hills alternated between a 2.6 KB stub and
# its full 109 KB listing on consecutive requests, and a single unlucky
# fetch was being recorded as "complete, 0 links, no error", which is
# indistinguishable from a school that genuinely has no openings.
EMPTY_RETRIES = 2
EMPTY_RETRY_WAIT = 8


def run_postings(mod):
    """Call the school's run directly rather than its main(), because main()
    closes the shared browser on the way out -- fine for one school on its
    own, ruinous when the next 800 want to reuse it."""
    if getattr(mod, 'PLATFORM', None):
        result = lib.run_platform_school(mod.SCHOOL_ID, mod.SCHOOL_NAME, mod.CAREERS_LINK,
                                         mod.CHECKPOINT_PATH, platform=mod.PLATFORM)
    else:
        result = lib.run_checkpointed(mod.SCHOOL_ID, mod.CHECKPOINT_PATH, mod.find_links)
    return result.get('status', ''), len(result.get('links', [])), result.get('last_error', '')


def run_info(mod):
    if hasattr(mod, 'fetch_detail'):
        result = jinfo.run_school_job_info(mod.SCHOOL_ID, mod.JOB_POSTINGS_CHECKPOINT,
                                           mod.CHECKPOINT_PATH,
                                           fetch_detail_fn=mod.fetch_detail,
                                           use_llm=getattr(mod, 'USE_LLM', False))
    else:
        platform = lib.detect_platform(mod.CAREERS_LINK)
        result = jinfo.run_school_job_info_bulk(mod.SCHOOL_ID, mod.CAREERS_LINK, platform,
                                                mod.JOB_POSTINGS_CHECKPOINT, mod.CHECKPOINT_PATH,
                                                use_llm=getattr(mod, 'USE_LLM', False))
    rows = result.get('rows', {})
    n_ok = sum(1 for r in rows.values() if 'error' not in r)
    return result.get('status', ''), n_ok, result.get('last_error', '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--stage', choices=['postings', 'info'], default='postings')
    ap.add_argument('--verdicts', default='',
                    help='only schools with these verification verdicts (e.g. "ok")')
    ap.add_argument('--timeout', type=int, default=240, help='seconds per school')
    ap.add_argument('--redo', action='store_true', help='re-run schools already complete')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    with open(MASTER, encoding='utf-8') as f:
        schools = [r for r in csv.DictReader(f) if r['country'] == args.country]

    wanted = {v.strip() for v in args.verdicts.split(',') if v.strip()}
    if wanted:
        vpath = VERIFY_FMT.format(country=args.country)
        if not os.path.exists(vpath):
            sys.exit(f'--verdicts needs {vpath}')
        with open(vpath, encoding='utf-8') as f:
            verdict_of = {r['school_id']: r['verdict'] for r in csv.DictReader(f)}
        schools = [s for s in schools if verdict_of.get(s['school_id']) in wanted]

    code_dir = POSTS_CODE if args.stage == 'postings' else INFO_CODE
    suffix = 'job_postings' if args.stage == 'postings' else 'job_info'
    runner = run_postings if args.stage == 'postings' else run_info

    todo = []
    for s in schools:
        path = os.path.join(code_dir, f"school_id_{s['school_id']}_{suffix}.py")
        if os.path.exists(path):
            todo.append((s, path))
    if args.limit:
        todo = todo[:args.limit]

    log_path = os.path.join(HERE, f'run_log_{args.country}_{args.stage}.csv')
    print(f'{args.country} {args.stage}: {len(todo)} schools to run '
          f'(timeout {args.timeout}s each)', flush=True)

    signal.signal(signal.SIGALRM, _alarm)
    rows = []
    started = time.time()
    counts = {'complete': 0, 'error': 0, 'timeout': 0, 'skipped': 0}
    total_links = 0

    for i, (s, path) in enumerate(todo, 1):
        sid = s['school_id']
        ckpt = os.path.join(code_dir, f'school_id_{sid}_{suffix}.checkpoint')
        if not args.redo and checkpoint_status(ckpt) == 'complete':
            counts['skipped'] += 1
            continue

        status = err = ''
        n = 0
        t0 = time.time()
        signal.alarm(args.timeout)
        try:
            mod = load_module(path, f'school_{sid}_{suffix}')
            status, n, err = runner(mod)
            for attempt in range(EMPTY_RETRIES):
                if n or status != 'complete':
                    break
                time.sleep(EMPTY_RETRY_WAIT)
                if os.path.exists(ckpt):
                    os.remove(ckpt)      # a stored empty result would short-circuit the retry
                status, n, err = runner(mod)
        except Timeout:
            status, err = 'timeout', f'exceeded {args.timeout}s'
        except Exception as e:
            status, err = 'error', f'{type(e).__name__}: {str(e)[:160]}'
            if os.environ.get('SCRAPE_DEBUG'):
                traceback.print_exc()
        finally:
            signal.alarm(0)

        if status not in ('complete',):
            # Never let one school's blown-up browser poison the rest.
            try:
                lib.close_browser()
            except Exception:
                pass

        counts[status if status in counts else 'error'] = \
            counts.get(status if status in counts else 'error', 0) + 1
        total_links += n
        rows.append({'school_id': sid, 'name': s['name'], 'status': status,
                     'count': n, 'seconds': round(time.time() - t0, 1), 'error': err})

        if i % 20 == 0 or status not in ('complete',):
            rate = i / max(time.time() - started, 1) * 60
            print(f"  [{i}/{len(todo)}] {status:9s} n={n:<5d} {s['name'][:36]:36s} "
                  f"({rate:.0f}/min)", flush=True)
        if i % 50 == 0:
            _write_log(log_path, rows)

    _write_log(log_path, rows)
    try:
        lib.close_browser()
    except Exception:
        pass

    mins = (time.time() - started) / 60
    print(f'\ndone in {mins:.0f} min -- wrote {log_path}')
    for k, v in sorted(counts.items()):
        if v:
            print(f'  {v:5d}  {k}')
    print(f'  {total_links} total {"links" if args.stage == "postings" else "rows"}')


def _write_log(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['school_id', 'name', 'status', 'count',
                                          'seconds', 'error'])
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
