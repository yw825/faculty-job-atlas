"""
Checks, for every school in a country, whether its recorded careers_link
actually reaches a page that LISTS job openings -- before any per-school
scraper is written against it.

Run from job-data/:
    python3 verify_careers_links.py US            # verify, write the report
    python3 verify_careers_links.py US --limit 50 # smoke-test a slice

Writes careers_link_verification_<country>.csv:
    school_id, name, careers_link, platform, verdict, n_links, note

WHY THIS EXISTS
The non-US set had its links checked by hand. The US set is 1,226 schools,
which is too many to eyeball, and a wrong link fails in ways that look like
success: a careers homepage returns HTTP 200 and plenty of <a> tags, so a
scraper written against it produces rows that are navigation rather than
jobs -- exactly the failure that put 778 rows titled "Page not found." into
the non-US data. So each link is judged on whether POSTINGS can actually be
pulled from it, not on whether it loads.

VERDICTS
    ok          postings were extracted from it (n_links says how many)
    empty       reached a real listing but it currently has no openings --
                genuinely possible, and NOT the same as a broken link
    review      loaded, but nothing posting-shaped came back
    broken      never loaded (DNS, timeout, 4xx/5xx), or is not a jobs URL
                at all (a social media page, say)

Shared tenants are fetched once and the result reused: 19 Penn State
campuses list against one Workday site, and hitting it 19 times would be
both slow and rude.
"""
import argparse
import concurrent.futures as futures
import csv
import os
import re
import sys
import threading
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')

# Hosts that are never a job listing, however well they load.
_NOT_A_JOBS_HOST = re.compile(
    r'(?:^|\.)(?:instagram|facebook|twitter|x|linkedin|youtube|tiktok)\.com$', re.I)

# Signs the page is a wall rather than a listing.
_WALL_RE = re.compile(
    r'\b(?:page not found|404 error|access denied|forbidden|'
    r'sign in to continue|please enable (?:javascript|cookies)|'
    r'just a moment|checking your browser|verify you are human|'
    r'complete the security check)\b', re.I)

_lock = threading.Lock()
_url_cache = {}


def classify_own_website_static(url):
    """Pure-HTTP first look. Returns (verdict, n, note) or None meaning
    "inconclusive, needs a rendered retry" -- which must happen on the main
    thread, because Playwright's sync API cannot be driven from a worker."""
    host = urlsplit(url).netloc.lower()
    if _NOT_A_JOBS_HOST.search(host):
        return 'broken', 0, f'not a jobs site ({host})'

    try:
        status, html = lib.fetch_static(url)
    except Exception as e:
        status, html = 0, ''
        note_fetch = f'{type(e).__name__}'
    else:
        note_fetch = ''

    if status and status >= 400:
        # NOT broken yet. A plain HTTP client gets 403 from plenty of sites
        # whose WAF simply doesn't like non-browser traffic, while a real
        # browser loads them fine -- confirmed live: 6 of 8 US schools first
        # recorded as "HTTP 403" scrape normally through Playwright. Hand it
        # to the rendered pass and let THAT decide.
        return None

    if not html or len(html) < 800:
        return None  # probably script-built; retry rendered, serially

    verdict = _judge(html, url, '')
    if verdict[0] == 'ok':
        return verdict
    return None  # anything less than a clear pass earns a rendered retry


def _judge(html, url, note):
    links = lib.extract_links(html, url, href_pattern=lib.COMMON_JOB_URL_HINTS,
                              text_pattern=lib.COMMON_JOB_URL_HINTS)
    n = len(set(links))
    if n >= 3:
        return 'ok', n, note
    if _WALL_RE.search(re.sub(r'<[^>]+>', ' ', html)[:4000]):
        return 'review', n, (note + ' wall/challenge page').strip()
    if n >= 1:
        return 'review', n, (note + ' few job-shaped links').strip()
    return 'review', 0, (note + ' no job-shaped links found').strip()


def classify_own_website_rendered(url, http_status=None):
    html = lib.fetch_rendered(url, wait_ms=3500) or ''
    if lib.is_fetch_failure(html) or not html:
        note = f'HTTP {http_status} and browser fetch failed' if http_status else 'fetch failed'
        return 'broken', 0, note
    verdict, n, note = _judge(html, url, 'rendered')
    if http_status and http_status >= 400:
        note = (note + f' (plain HTTP said {http_status})').strip()
    return verdict, n, note


def classify(school):
    url = school['careers_link'].strip()
    if not url:
        return 'broken', 0, 'no careers_link recorded'

    with _lock:
        cached = _url_cache.get(url)
    if cached:
        verdict, n, note = cached
        return verdict, n, (note + ' [shared URL]').strip()

    platform = lib.detect_platform(url)
    try:
        if platform and platform in lib.PLATFORM_ADAPTERS:
            links = lib.PLATFORM_ADAPTERS[platform](url, school['name'])
            n = len(set(links))
            result = ('ok', n, platform) if n else ('empty', 0, f'{platform} returned 0')
        else:
            result = classify_own_website(url)
    except Exception as e:
        result = ('broken', 0, f'{type(e).__name__}: {str(e)[:70]}')

    with _lock:
        _url_cache[url] = result
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--recheck', default='',
                    help='re-check only schools whose PREVIOUS verdict was one of these '
                         '(e.g. "broken"), merging the result into the existing report')
    args = ap.parse_args()

    with open(MASTER, encoding='utf-8') as f:
        schools = [r for r in csv.DictReader(f) if r['country'] == args.country]
    previous = {}
    out_path_existing = os.path.join(HERE, f'careers_link_verification_{args.country}.csv')
    if args.recheck and os.path.exists(out_path_existing):
        with open(out_path_existing, encoding='utf-8') as f:
            previous = {r['school_id']: r for r in csv.DictReader(f)}
        want = {v.strip() for v in args.recheck.split(',') if v.strip()}
        schools = [s for s in schools
                   if previous.get(s['school_id'], {}).get('verdict') in want]
        print(f'rechecking {len(schools)} previously-{"/".join(sorted(want))} schools',
              flush=True)
    if args.limit:
        schools = schools[:args.limit]

    results = {}
    platform_of = {}
    for s in schools:
        platform_of[s['school_id']] = lib.detect_platform(s['careers_link']) or 'own website'

    own = [s for s in schools if platform_of[s['school_id']] == 'own website']
    plat = [s for s in schools if platform_of[s['school_id']] != 'own website']
    print(f'{args.country}: {len(schools)} schools -- {len(own)} own-website, '
          f'{len(plat)} on a known platform', flush=True)

    # ---- pass 1: pure HTTP, safe to parallelise -------------------------
    needs_render = []
    print(f'pass 1: static check of {len(own)} own-website links '
          f'({args.workers} at a time)', flush=True)
    done = 0

    def static_one(s):
        url = s['careers_link'].strip()
        if not url:
            return 'broken', 0, 'no careers_link recorded'
        if _NOT_A_JOBS_HOST.search(urlsplit(url).netloc.lower()):
            return 'broken', 0, f'not a jobs site ({urlsplit(url).netloc})'
        with _lock:
            if url in _url_cache:
                v, n, note = _url_cache[url]
                return v, n, (note + ' [shared URL]').strip()
        try:
            out = classify_own_website_static(url)
        except Exception as e:
            return 'broken', 0, f'{type(e).__name__}: {str(e)[:70]}'
        if out is None:
            return None
        with _lock:
            _url_cache[url] = out
        return out

    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fut_map = {pool.submit(static_one, s): s for s in own}
        for fut in futures.as_completed(fut_map):
            s = fut_map[fut]
            try:
                out = fut.result()
            except Exception as e:
                out = ('broken', 0, f'{type(e).__name__}')
            if out is None:
                needs_render.append(s)
            else:
                results[s['school_id']] = out
            done += 1
            if done % 50 == 0:
                print(f'  {done}/{len(own)}', flush=True)

    # ---- pass 2: browser + platform adapters, serial on the main thread --
    serial = plat + needs_render
    print(f'pass 2: {len(serial)} needing a browser or a platform adapter '
          f'({len(plat)} platform, {len(needs_render)} rendered retries)', flush=True)
    for i, s in enumerate(serial, 1):
        url = s['careers_link'].strip()
        pf = platform_of[s['school_id']]
        if url in _url_cache:
            v, n, note = _url_cache[url]
            results[s['school_id']] = (v, n, (note + ' [shared URL]').strip())
        else:
            try:
                if pf != 'own website':
                    links = lib.PLATFORM_ADAPTERS[pf](url, s['name'])
                    n = len(set(links))
                    out = ('ok', n, pf) if n else ('empty', 0, f'{pf} returned 0')
                else:
                    out = classify_own_website_rendered(url)
            except Exception as e:
                out = ('broken', 0, f'{type(e).__name__}: {str(e)[:70]}')
            _url_cache[url] = out
            results[s['school_id']] = out
        if i % 25 == 0:
            print(f'  {i}/{len(serial)}', flush=True)

    rows = []
    for s in schools:
        verdict, n, note = results.get(s['school_id'], ('review', 0, 'not checked'))
        rows.append({'school_id': s['school_id'], 'name': s['name'],
                     'careers_link': s['careers_link'], 'platform': platform_of[s['school_id']],
                     'verdict': verdict, 'n_links': n, 'note': note})
    if previous:
        merged = dict(previous)
        for r in rows:
            merged[r['school_id']] = r
        rows = list(merged.values())
    rows.sort(key=lambda r: int(r['school_id']))

    out_path = os.path.join(HERE, f'careers_link_verification_{args.country}.csv')
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['school_id', 'name', 'careers_link', 'platform',
                                          'verdict', 'n_links', 'note'])
        w.writeheader()
        w.writerows(rows)

    tally = {}
    for r in rows:
        tally[r['verdict']] = tally.get(r['verdict'], 0) + 1
    print(f'\nwrote {out_path}')
    for k in ('ok', 'empty', 'review', 'broken'):
        if k in tally:
            print(f'  {tally[k]:5d}  {k}')
    print(f'  {sum(int(r["n_links"] or 0) for r in rows)} postings visible across all links')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
