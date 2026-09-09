"""
Adds the missing SiteId to stored PeopleSoft posting URLs.

Run from job-data/:
    python3 repair_peoplesoft_siteid.py --dry-run
    python3 repair_peoplesoft_siteid.py

WHY
A PeopleSoft deep link needs the SiteId to resolve to the job. Without it
the same URL renders the generic "Careers" search scaffolding, so the map
carries a link that opens the wrong page while the title beside it is
right -- reported on University of Puget Sound's "Assistant Professor of
Business Analytics".

Two ways the id went missing. Puget Sound and Central Washington spell the
parameter "siteid" in their careers link and the lookup was case-sensitive
(fixed in peoplesoft_posting_url). Toronto Metropolitan's careers link
carries no site id at all, so it has to be discovered by trying candidates
and seeing which renders a job page.

Every school is verified before anything is written: one repaired URL is
opened and must show a real posting ("Job Description"/"Apply for Job"),
otherwise that school is left alone and reported.
"""
import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')
CANDIDATES = ['1', '2', '3', '4', '40000']


def renders_a_job(url):
    html = lib.fetch_rendered(url, wait_ms=9000) or ''
    if lib.is_fetch_failure(html):
        return False
    from bs4 import BeautifulSoup
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    return ('Job Description' in text or 'Apply for Job' in text) and 'Search Jobs' not in text[:80]


def site_id_for(careers_link, sample_url):
    """From the careers link if it names one, else by trying candidates."""
    from urllib.parse import urlsplit, parse_qs
    q = {k.lower(): v for k, v in parse_qs(urlsplit(careers_link).query).items()}
    known = (q.get('siteid') or [''])[0]
    order = ([known] if known else []) + [c for c in CANDIDATES if c != known]
    for candidate in order:
        if renders_a_job(f'{sample_url}&SiteId={candidate}'):
            return candidate
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--ids-file', default='/tmp/ps_fix.json')
    args = ap.parse_args()

    master = {r['school_id']: r for r in csv.DictReader(open(MASTER))}
    ids = [str(i) for i in json.load(open(args.ids_file))]
    fixed = skipped = 0
    for sid in ids:
        school = master.get(sid)
        path = os.path.join(HERE, 'school_job_posts', f'school_id_{sid}_job_posts.csv')
        if not school or not os.path.exists(path):
            continue
        rows = list(csv.DictReader(open(path)))
        need = [r for r in rows if 'siteid=' not in r['post_link'].lower()]
        if not need:
            continue
        site = site_id_for(school['careers_link'], need[0]['post_link'])
        if not site:
            print(f'  [{sid}] {school["name"][:30]:30s} no SiteId renders a job -- left alone')
            skipped += 1
            continue
        for r in rows:
            if 'siteid=' not in r['post_link'].lower():
                r['post_link'] = r['post_link'] + f'&SiteId={site}'
        print(f'  [{sid}] {school["name"][:30]:30s} SiteId={site} applied to {len(need)} links')
        fixed += len(need)
        if args.dry_run:
            continue
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['school_id', 'post_link'])
            w.writeheader()
            w.writerows(rows)
        ck = os.path.join(HERE, 'school_job_posts_code',
                          f'school_id_{sid}_job_postings.checkpoint')
        if os.path.exists(ck):
            try:
                d = json.load(open(ck))
                d['links'] = [u if 'siteid=' in u.lower() else u + f'&SiteId={site}'
                              for u in d.get('links', [])]
                json.dump(d, open(ck, 'w'))
            except Exception:
                pass

    print(f'{"would repair" if args.dry_run else "repaired"} {fixed} links; {skipped} schools left alone')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
