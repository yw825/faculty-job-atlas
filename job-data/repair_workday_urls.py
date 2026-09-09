"""
Rewrites Workday posting URLs that are missing their site segment, in the
posts and info CSVs, without re-scraping.

Run from job-data/:
    python3 repair_workday_urls.py --dry-run
    python3 repair_workday_urls.py

WHY
The Workday jobs API returns each posting's externalPath relative to the
SITE ("/job/NTU-Main-Campus-Singapore/Postdoctoral-Fellow_R00025733"), not
to the host root. scrape_workday joined it against the host alone, so every
posting it ever recorded was stored as

    https://ntu.wd3.myworkdayjobs.com/job/...          -> 404

instead of

    https://ntu.wd3.myworkdayjobs.com/Careers/job/...  -> 200

13,011 links across 175 schools -- roughly 40% of the map -- were dead on
click. It went unnoticed because job_info reads Workday postings through
the CXS API rather than by opening the page, so the rows themselves look
healthy; only a reader clicking through ever met the 404.

The site segment is recoverable from each school's careers_link, so the
stored URLs are repaired in place rather than by re-scraping 175 schools.
Every school's rewrite is verified by fetching one repaired URL first: if
it does not answer 200, that school is left untouched and reported.
"""
import argparse
import csv
import glob
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')
BROKEN_RE = re.compile(r'^(https://[^/]+)/job/(.*)$')


def public_base(careers_link):
    """The site-rooted base a posting's externalPath hangs off."""
    parsed = urlparse(careers_link)
    path_parts = [p for p in parsed.path.split('/') if p]
    path_parts = [p for p in path_parts if not re.fullmatch(r'[a-z]{2}(-[A-Z]{2})?', p)]
    if 'myworkdaysite.com' in parsed.netloc:
        if len(path_parts) < 2:
            return None
        return f'https://{parsed.netloc}/recruiting/{path_parts[-2]}/{path_parts[-1]}'
    if not path_parts:
        return None
    return f'https://{parsed.netloc}/{path_parts[0]}'


def repair(url, base):
    m = BROKEN_RE.match(url)
    if not m:
        return url
    return f'{base}/job/{m.group(2)}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    master = {r['school_id']: r for r in csv.DictReader(open(MASTER))}
    fixed_rows = fixed_schools = 0
    unverified = []

    for path in sorted(glob.glob(os.path.join(HERE, 'school_job_posts', '*_job_posts.csv'))):
        sid = os.path.basename(path).split('_')[2]
        school = master.get(sid)
        if not school:
            continue
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)
        broken = [r for r in rows if BROKEN_RE.match(r.get('post_link', ''))
                  and 'myworkday' in r.get('post_link', '')]
        if not broken:
            continue
        base = public_base(school['careers_link'])
        if not base:
            unverified.append((sid, 'no site segment in careers_link'))
            continue

        sample = repair(broken[0]['post_link'], base)
        try:
            status, _body = lib.fetch_static(sample)
        except Exception:
            status = None
        if status != 200:
            unverified.append((sid, f'sample repaired URL returned {status}'))
            continue

        for r in rows:
            if 'myworkday' in r.get('post_link', ''):
                r['post_link'] = repair(r['post_link'], base)
        fixed_rows += len(broken)
        fixed_schools += 1
        if not args.dry_run:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)

        # The job_postings CHECKPOINT is what job_info actually reads, so it
        # has to be repaired too -- otherwise the next info run rebuilds the
        # broken URLs from it and quietly undoes this.
        ckpt = os.path.join(HERE, 'school_job_posts_code',
                            f'school_id_{sid}_job_postings.checkpoint')
        if os.path.exists(ckpt) and not args.dry_run:
            try:
                import json
                with open(ckpt, encoding='utf-8') as f:
                    data = json.load(f)
                data['links'] = [repair(u, base) if 'myworkday' in u else u
                                 for u in data.get('links', [])]
                with open(ckpt, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            except Exception:
                pass

        info_path = os.path.join(HERE, 'school_job_info', f'school_id_{sid}_job_info.csv')
        if os.path.exists(info_path):
            with open(info_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                ifields = reader.fieldnames
                irows = list(reader)
            for r in irows:
                if 'myworkday' in (r.get('posting_url') or ''):
                    r['posting_url'] = repair(r['posting_url'], base)
            if not args.dry_run and irows:
                with open(info_path, 'w', newline='', encoding='utf-8') as f:
                    w = csv.DictWriter(f, fieldnames=ifields)
                    w.writeheader()
                    w.writerows(irows)

    verb = 'would repair' if args.dry_run else 'repaired'
    print(f'{verb} {fixed_rows} Workday posting URLs across {fixed_schools} schools')
    if unverified:
        print(f'{len(unverified)} schools left untouched (repair not verifiable):')
        for sid, why in unverified[:15]:
            print(f'   [{sid}] {why}')


if __name__ == '__main__':
    main()
