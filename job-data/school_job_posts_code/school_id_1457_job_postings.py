"""
Job postings scraper for school_id 1457 - Virginia Polytechnic Institute and State University
ATS platform: own website
Careers link: https://jobs.apply.vt.edu/jobs/search?page=1&employment_type_uids%5B%5D=beaf2a59c21052585454b659fedb9e7a&employment_type_uids%5B%5D=9656b3af311ae5c9e88673da8bb39af5

The PageUp link returned only navigation pages.

TUNED FIND_LINKS
Career-pages board, paged; the link's filters are kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1457
SCHOOL_NAME = 'Virginia Polytechnic Institute and State University'
CAREERS_LINK = 'https://jobs.apply.vt.edu/jobs/search?page=1&employment_type_uids%5B%5D=beaf2a59c21052585454b659fedb9e7a&employment_type_uids%5B%5D=9656b3af311ae5c9e88673da8bb39af5'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://jobs\.apply\.vt\.edu/jobs/(?!search)[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# jobs.apply.vt.edu sits behind an AWS WAF and injects its rows into
# #jobs_search_results_<hash> after load, so a plain fetch sees nothing and the
# old PageUp link returned only navigation (photo-tour.html, veterans.html).
LISTING = 'https://jobs.apply.vt.edu/jobs/search/search-page-faculty'
POSTING = re.compile(r'https://jobs\.apply\.vt\.edu/jobs/[a-z0-9][a-z0-9\-]{10,90}')
RENDER_WAIT_MS = 11000      # the rows arrive well after domcontentloaded


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
