"""
Job postings scraper for school_id 15 - University of West Alabama (US)
ATS platform: own website
Careers link: https://www.uwa.edu/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of West Alabama; nothing here affects any
other school's script.

Link check (review): 2 posting-shaped links found -- rendered few job-shaped links.

TUNED FIND_LINKS
Two kinds of opening: leadership searches announced as pages named
/the-university-of-west-alabama-seeks-<role>/, and everything else on UWA's
Interfolio board (tenant 16278), which the page embeds as a widget. The board
is read through the Interfolio API rather than the rendered widget; both
returned the same 44 postings on 2026-10-07.

Writes school_job_posts/school_id_15_job_posts.csv (school_id, post_link).
Checkpointed to school_id_15_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 15
SCHOOL_NAME = 'University of West Alabama'
CAREERS_LINK = 'https://www.uwa.edu/employment/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://(?:www\.uwa\.edu/the-university-of-west-alabama-seeks-[^/?#]+/?|apply\.interfolio\.com/\d+)$', re.I)


SEARCH_PAGE_RE = re.compile(r'^https://www\.uwa\.edu/the-university-of-west-alabama-seeks-[^/?#]+/?$', re.I)
INTERFOLIO_BOARD = 'https://apply.interfolio.com/16278'


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    searches = [u for u in lib.extract_links(html, CAREERS_LINK) if SEARCH_PAGE_RE.search(u)]
    return searches + lib.scrape_interfolio(INTERFOLIO_BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
