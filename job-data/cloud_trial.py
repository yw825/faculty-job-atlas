"""Dry-run a sample of schools' link finders and compare with stored counts.

Answers "can this board be scraped from a cloud machine?" before the daily
refresh moves to GitHub Actions. Nothing is saved: find_links() is called
directly and only the number of links is compared with the school's
current checkpoint.

    python3 cloud_trial.py --sample 100 --out trial.csv
    python3 cloud_trial.py --ids 425,429,502
"""
import argparse
import csv
import importlib.util
import json
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

REAL_CHROME = ['425', '429', '502', '1052', '1590', '1594', '1715']


class Timeout(Exception):
    pass


def _alarm(*_):
    raise Timeout()


def stored_count(sid):
    try:
        with open(os.path.join(HERE, 'school_job_posts_code',
                               f'school_id_{sid}_job_postings.checkpoint'), encoding='utf-8') as f:
            return len(json.load(f).get('links', []))
    except (OSError, ValueError):
        return None


def sample_ids(n):
    with open(os.path.join(HERE, 'schools_master.csv'), encoding='utf-8') as f:
        ids = [r['school_id'] for r in csv.DictReader(f)]
    ids = [i for i in ids if os.path.exists(os.path.join(
        HERE, 'school_job_posts_code', f'school_id_{i}_job_postings.py'))]
    step = max(1, len(ids) // n)
    picked = ids[::step][:n]
    return picked + [i for i in REAL_CHROME if i not in picked]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=100)
    ap.add_argument('--ids', default='')
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--out', default='trial.csv')
    args = ap.parse_args()
    ids = [i for i in args.ids.split(',') if i] or sample_ids(args.sample)

    signal.signal(signal.SIGALRM, _alarm)
    rows = []
    for k, sid in enumerate(ids, 1):
        path = os.path.join(HERE, 'school_job_posts_code', f'school_id_{sid}_job_postings.py')
        t0, n, err = time.time(), None, ''
        signal.alarm(args.timeout)
        try:
            spec = importlib.util.spec_from_file_location(f'trial_{sid}', path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'find_links'):
                n = len(mod.find_links())
            else:
                n = len(lib.PLATFORM_ADAPTERS[mod.PLATFORM](mod.CAREERS_LINK, mod.SCHOOL_NAME))
        except BaseException as e:
            err = f'{type(e).__name__}: {str(e)[:150]}'.replace('\n', ' ')
            lib.reset_browser()
        finally:
            signal.alarm(0)
        stored = stored_count(sid)
        if n is None:
            verdict = 'FAILED'
        elif stored and n == 0:
            verdict = 'EMPTY'
        elif stored and n < 0.75 * stored:
            verdict = 'SHORT'
        else:
            verdict = 'ok'
        rows.append({'school_id': sid, 'stored': stored, 'cloud': n, 'verdict': verdict,
                     'seconds': round(time.time() - t0), 'error': err})
        print(f'[{k}/{len(ids)}] {sid:>5} stored={stored} cloud={n} {verdict} {err[:80]}', flush=True)
    try:
        lib.close_browser()
    except Exception:
        pass

    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r['verdict']] = counts.get(r['verdict'], 0) + 1
    print('summary:', counts)


if __name__ == '__main__':
    main()
