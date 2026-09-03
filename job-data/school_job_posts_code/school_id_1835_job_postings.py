"""
Job postings scraper for school_id 1835 - Hong Kong Chu Hai College (Hong Kong)
ATS platform: own website
Careers link: https://www.chuhai.edu.hk/en/page/jobs?id=b9f07df8-bc36-430a-91ea-b8f196e36f18

CUSTOMIZED (confirmed live): the careers link is itself one of four
CATEGORY pages ("Research / Project Positions", "Administrative Positions",
"Academic Positions" -- the careers link itself, "Management Positions"),
all sharing the exact same "/jobs?id=<guid>" URL shape as individual
postings, with each category page showing that category's posting(s)
directly inline (no further click needed) or "Currently no job opening for
this position" when empty. The generic default only picked up the 3 OTHER
category nav links visible from this page, missing the careers link's own
content (a real posting) entirely, while also keeping the empty
"Management Positions" category as if it were a posting.

Confirmed live: as of this writing, Research/Project's one posting page
covers 3 headcounts in a single text block with no distinct link per
headcount ("Research Fellow/Research Associate (3 headcounts...)") -- the
CSV schema here is one row per URL, so that page is still one row; there is
no way to represent 3 headcounts as 3 distinct posting_urls without a
per-headcount link existing on the page, which it doesn't.

Writes school_job_posts/school_id_1835_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1835_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1835
SCHOOL_NAME = 'Hong Kong Chu Hai College'
CAREERS_LINK = 'https://www.chuhai.edu.hk/en/page/jobs?id=b9f07df8-bc36-430a-91ea-b8f196e36f18'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

CATEGORY_LINK_RE = re.compile(r'/jobs\?id=')
NO_OPENING_RE = re.compile(r'currently no job opening', re.I)


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    category_pages = [CAREERS_LINK] + lib.extract_links(html, CAREERS_LINK, href_pattern=CATEGORY_LINK_RE)
    links = []
    for url in category_pages:
        page_html = html if url == CAREERS_LINK else lib.fetch_rendered(url)
        if lib.is_fetch_failure(page_html):
            continue
        text = BeautifulSoup(page_html, 'html.parser').get_text(' ', strip=True)
        if not NO_OPENING_RE.search(text):
            links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
