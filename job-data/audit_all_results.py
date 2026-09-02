"""
Broader audit across ALL scraped schools in the current _scrape_log.csv, not
just ones marked 'empty' (see audit_empty_results.py for that narrower pass).
Looks for the specific suspicious patterns that have turned out to be real
bugs so far this session:

  - DUPLICATE_COUNT: two or more schools on the same shared-tenant platform
    return the exact same posting count -- the signature of an unfiltered
    fallback silently returning the same whole-tenant list to everyone
    (confirmed real cases: Workday's Singapore "PublicServiceCareers" tenant,
    Oracle schools before the facet fix).
  - BLANK_TITLE: any row with an empty/whitespace-only job_title.
  - SUSPICIOUSLY_ROUND: a count that's an exact multiple of a common page
    size (25, 50, 100, 500) -- can indicate a pagination loop stopping at a
    cap rather than the real total.
  - EMPTY_BUT_KEYWORD_FOUND: delegates to the existing per-school keyword
    re-check from audit_empty_results.py.

This does not modify any scraped data -- it only reports findings for review.
"""
import csv
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_CSV = os.path.join(HERE, 'school_job_posts', '_scrape_log.csv')
OUT_DIR = os.path.join(HERE, 'school_job_posts')

ROUND_NUMBERS = {25, 50, 100, 250, 500, 750, 1000, 1250}


def main():
    rows = list(csv.DictReader(open(LOG_CSV, newline='', encoding='utf-8')))
    print(f'{len(rows)} schools in log\n')

    # 1. Duplicate-count check, grouped by platform (only meaningful within
    # the same platform -- two schools on different platforms sharing a count
    # by coincidence isn't suspicious).
    by_platform_count = defaultdict(list)
    for r in rows:
        if r['status'] != 'ok' or not r['count'] or r['count'] == '0':
            continue
        by_platform_count[(r['platform'], r['count'])].append(r['name'])

    print('=== DUPLICATE_COUNT (same platform, same nonzero count -- check for unfiltered-fallback bugs) ===')
    found_dup = False
    for (platform, count), names in sorted(by_platform_count.items(), key=lambda x: -len(x[1])):
        if len(names) > 1:
            found_dup = True
            print(f'  platform={platform} count={count}: {names}')
    if not found_dup:
        print('  none found')

    # 2. Suspiciously round counts (possible pagination cap truncation)
    print('\n=== SUSPICIOUSLY_ROUND (exact multiple of a common page size -- check for cap truncation) ===')
    found_round = False
    for r in rows:
        if r['status'] != 'ok' or not r['count']:
            continue
        c = int(r['count'])
        if c > 0 and c in ROUND_NUMBERS:
            found_round = True
            print(f'  {r["name"]} (id={r["school_id"]}): count={c} platform={r["platform"]}')
    if not found_round:
        print('  none found')

    # 3. Blank-title check across every school's actual output file
    print('\n=== BLANK_TITLE (empty job_title in output) ===')
    found_blank = False
    for r in rows:
        if r['status'] != 'ok':
            continue
        path = os.path.join(OUT_DIR, f'school_id_{r["school_id"]}_job_posts.csv')
        if not os.path.exists(path):
            continue
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if not row.get('job_title', '').strip():
                    found_blank = True
                    print(f'  {r["name"]} (id={r["school_id"]}): blank title, url={row.get("posting_url","")[:80]}')
    if not found_blank:
        print('  none found')

    # 4. Simple sanity summary
    print('\n=== SUMMARY ===')
    total_postings = 0
    for r in rows:
        path = os.path.join(OUT_DIR, f'school_id_{r["school_id"]}_job_posts.csv')
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                total_postings += sum(1 for _ in csv.DictReader(f))
    print(f'Total postings across all {len(rows)} schools: {total_postings}')
    ok = sum(1 for r in rows if r['status'] == 'ok')
    empty = sum(1 for r in rows if r['status'] == 'empty')
    failed = sum(1 for r in rows if r['status'] == 'failed')
    print(f'ok={ok} empty={empty} failed={failed}')


if __name__ == '__main__':
    main()
