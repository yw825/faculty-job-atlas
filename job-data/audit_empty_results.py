"""
Double-checks EVERY school logged as status='empty' by scrape_job_postings.py --
not a sample. For each, re-fetches the page (and any department-hop targets it
would have followed) and checks whether ANY academic-position keyword appears
anywhere in the raw text, in any of the ~12 supported languages, with no gating
by URL shape or title length at all (the loosest possible check).

If a keyword appears anywhere but the real scraper still found 0 postings, that
page is flagged SUSPICIOUS and printed with surrounding context for a real,
individual fix -- not waved through. If no academic keyword appears anywhere,
the empty result is marked LIKELY_GENUINE and left alone.

This is a review tool, not a fix -- it does not modify school_job_posts/*.csv.
It writes a report so every empty result has an explicit, auditable verdict.
"""
import csv
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_job_postings as s

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_CSV = os.path.join(HERE, 'school_job_posts', '_scrape_log.csv')
REPORT_CSV = os.path.join(HERE, 'school_job_posts', '_empty_audit_report.csv')
MASTER_CSV = os.path.join(HERE, 'schools_master.csv')

ANY_KEYWORD_RE = s.POSITIVE_TITLE_RE  # already unions all 12 languages, loosest check needed


def load_school_urls():
    rows = {}
    with open(MASTER_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows[int(row['school_id'])] = row
    return rows


def audit_one(school_id, name, url):
    """Returns (verdict, detail) -- re-fetches independent of the real run's cache."""
    try:
        captures, fetcher = s.fetch_html_smart(url)
    except Exception as e:
        return 'AUDIT_ERROR', f'{type(e).__name__}: {e}'

    all_text_blobs = []
    urls_checked = [url]
    for html, _tab in captures:
        all_text_blobs.append((url, html))

    # Also check department-hop targets, same as the real scraper would have.
    for html, _tab in captures:
        hops = s.find_department_hop_links(html, url, set(urls_checked))
        for hop_url in hops[:5]:
            urls_checked.append(hop_url)
            try:
                hop_captures, _ = s.fetch_html_smart(hop_url)
                for hop_html, _ht in hop_captures:
                    all_text_blobs.append((hop_url, hop_html))
            except Exception:
                continue

    for page_url, html in all_text_blobs:
        if s.BOT_CHALLENGE_RE.search(html):
            return 'BLOCKED', f'bot-challenge page at {page_url}'
        soup = s.BeautifulSoup(html, 'html.parser')
        text = soup.get_text(' ', strip=True)
        m = ANY_KEYWORD_RE.search(text)
        if m:
            idx = m.start()
            context = text[max(0, idx - 80):idx + 120]
            return 'SUSPICIOUS', f'keyword "{m.group(0)}" found on {page_url} -- context: ...{context}...'

    return 'LIKELY_GENUINE', f'no academic keyword found across {len(all_text_blobs)} page(s) checked ({urls_checked})'


def main():
    if not os.path.exists(LOG_CSV):
        print('No scrape log found yet -- run the scraper first.')
        return
    school_urls = load_school_urls()
    empties = []
    with open(LOG_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['status'] == 'empty':
                empties.append(row)
    print(f'{len(empties)} empty results to double-check (not sampled -- all of them)')

    results = []
    for i, row in enumerate(empties, 1):
        sid = int(row['school_id'])
        name = row['name']
        school_row = school_urls.get(sid)
        if not school_row:
            continue
        url = school_row['careers_link']
        verdict, detail = audit_one(sid, name, url)
        results.append({'school_id': sid, 'name': name, 'url': url, 'verdict': verdict, 'detail': detail})
        print(f'[{i}/{len(empties)}] {name} (id={sid}) -> {verdict}  {detail[:150]}', flush=True)

    with open(REPORT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['school_id', 'name', 'url', 'verdict', 'detail'])
        writer.writeheader()
        writer.writerows(results)

    from collections import Counter
    counts = Counter(r['verdict'] for r in results)
    print()
    print('=== SUMMARY ===')
    for verdict, count in counts.most_common():
        print(f'  {verdict}: {count}')
    print(f'Full report: {REPORT_CSV}')


if __name__ == '__main__':
    main()
