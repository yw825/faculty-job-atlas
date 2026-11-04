"""
Fetches EVERY posting link of every school in a country set and records
whether it is actually a job posting.

Run from job-data/:
    python3 verify_posting_links.py --non-us
    python3 verify_posting_links.py --ids-file /tmp/ids.json

Writes posting_link_verification.csv:
    school_id, name, country, url, status, title, verdict

WHY EVERY LINK RATHER THAN A SAMPLE
Earlier passes checked one link per school, or matched titles against
patterns. Both miss the case this is for: a school whose link set is
mostly real with a handful of listing pages, feeds or dead links mixed in.
Bowdoin looked healthy by sample and still had two Atom feeds on the map.

VERDICTS
    posting      fetched, and nothing marks it as furniture
    dead         4xx/5xx (excluding the blocks below)
    blocked      401/403/429 -- the link may be fine, the fetch is refused
    furniture    a feed, search page, share widget or category URL, or a
                 page whose title is a careers site's own chrome
    unreachable  no response

Deliberately conservative: a page is called furniture only on positive
evidence, never because its text failed an English-language test. Most of
this set is not in English, so "doesn't look like a posting to me" is not
grounds to delete a school's row.
"""
import argparse
import concurrent.futures as futures
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib
import build_map_data as bmd
import clean_job_posts as cjp

MASTER = os.path.join(HERE, 'schools_master.csv')


def title_of(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in ('h1', 'title'):
        el = soup.find(tag)
        if el:
            t = el.get_text(' ', strip=True)
            if t:
                return t[:160]
    return ''


def check(item):
    sid, name, country, url, careers = item
    from urllib.parse import urlsplit
    # URL-shape furniture needs no fetch at all.
    if cjp._NEVER_A_POSTING.search(url):
        return (sid, name, country, url, '', '', 'furniture')
    if url.rstrip('/') == (careers or '').rstrip('/'):
        return (sid, name, country, url, '', '', 'furniture')
    try:
        status, html = lib.fetch_static(url)
    except Exception:
        return (sid, name, country, url, '', '', 'unreachable')
    if status is None:
        return (sid, name, country, url, '', '', 'unreachable')
    if status in (401, 403, 429):
        return (sid, name, country, url, status, '', 'blocked')
    if status >= 400:
        return (sid, name, country, url, status, '', 'dead')
    title = title_of(html or '')
    if title and bmd._JUNK_TITLE_RE.match(title.strip().rstrip(' .')):
        return (sid, name, country, url, status, title, 'furniture')
    return (sid, name, country, url, status, title, 'posting')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--non-us', action='store_true')
    ap.add_argument('--ids-file')
    ap.add_argument('--workers', type=int, default=20)
    ap.add_argument('--out', default='posting_link_verification.csv')
    args = ap.parse_args()

    master = {r['school_id']: r for r in csv.DictReader(open(MASTER))}
    if args.ids_file:
        ids = [str(i) for i in json.load(open(args.ids_file))]
    else:
        ids = [s for s, r in master.items() if r['country'] != 'US']

    work = []
    for sid in ids:
        s = master.get(sid)
        if not s:
            continue
        p = os.path.join(HERE, 'school_job_posts', f'school_id_{sid}_job_posts.csv')
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                u = (r.get('post_link') or '').strip()
                if u:
                    work.append((sid, s['name'], s['country'], u, s['careers_link']))
    print(f'verifying {len(work)} links across '
          f'{len({w[0] for w in work})} schools', flush=True)

    rows = []
    done = 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for res in pool.map(check, work):
            rows.append(res)
            done += 1
            if done % 500 == 0:
                print(f'  {done}/{len(work)}', flush=True)

    out = os.path.join(HERE, args.out)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['school_id', 'name', 'country', 'url', 'status', 'title', 'verdict'])
        w.writerows(rows)

    import collections
    tally = collections.Counter(r[6] for r in rows)
    print(f'\nwrote {out}')
    for k, v in tally.most_common():
        print(f'  {v:6d}  {k}')


if __name__ == '__main__':
    main()
