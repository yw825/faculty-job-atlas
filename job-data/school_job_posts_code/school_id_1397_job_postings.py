"""
Job postings scraper for school_id 1397 - University of Houston (US)
ATS platform: own website (PageUp career site)
Careers link: https://careers.uh.edu/jobs/search?page=1&category_uids%5B%5D=db3c1fb9609f486fa85f3e228dd5f7e2&category_uids%5B%5D=d3b80de9ada098478edbd5589a0ffeee&dropdown_field_1_uids%5B%5D=ec5c8a258322f40341774cadcfac91f9

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

The careers link was www.uh.edu/human-resources/careers/, an HR information
page, so the school collected five navigation links. The board is
careers.uh.edu.

It is the same PageUp career-site product as James Madison's and Kenyon's:
postings render only under /jobs/search, only after the page's own JS runs,
and each posting's URL is a pure SLUG with no numeric id
(/jobs/assistant-professor-sedimentology-and-stratigraphy-houston-texas-
united-states), so id-shaped patterns find nothing. Matching the slug path
is what works -- 30 postings, faculty among them.

/jobs/search/uh-postings returns the same 30, so the plain search path is
used here.

Writes school_job_posts/school_id_1397_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1397_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Career-pages board, paged; the link's filters are kept.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1397
SCHOOL_NAME = 'University of Houston'
CAREERS_LINK = 'https://careers.uh.edu/jobs/search?page=1&category_uids%5B%5D=db3c1fb9609f486fa85f3e228dd5f7e2&category_uids%5B%5D=d3b80de9ada098478edbd5589a0ffeee&dropdown_field_1_uids%5B%5D=ec5c8a258322f40341774cadcfac91f9'
ATS_PLATFORM = 'own website'

HOST = 'careers.uh.edu'
POSTING_PATH = re.compile(r'^/jobs/(?!search\b)[a-z0-9][a-z0-9\-]{8,200}$', re.I)
RENDER_WAIT_MS = 16000

POSTING_RE = re.compile(r'^https://careers\.uh\.edu/jobs/(?!search)[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
