"""
Job postings scraper for school_id 1188 - Drexel University (US)
ATS platform: own website
Careers link: https://careers.drexel.edu/jobs/search?_gl=1%2Anfs5qz%2A_ga%2AODM4MTgzMzQ3LjE3Mzk1MDA1ODM.%2A_ga_6KJ1PNLE19%2AczE3OTI0Mzc4MjMkbzE2MyRnMCR0MTc5MjQzNzgyMyRqNjAkbDAkaDA.

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Drexel University; nothing here affects any
other school's script.

Link check (ok): 20 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1188_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1188_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Drexel's board, paged.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1188
SCHOOL_NAME = 'Drexel University'
CAREERS_LINK = 'https://careers.drexel.edu/jobs/search?_gl=1%2Anfs5qz%2A_ga%2AODM4MTgzMzQ3LjE3Mzk1MDA1ODM.%2A_ga_6KJ1PNLE19%2AczE3OTI0Mzc4MjMkbzE2MyRnMCR0MTc5MjQzNzgyMyRqNjAkbDAkaDA.'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://careers\.drexel\.edu/jobs/(?!search)[a-z0-9-]+$')

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
