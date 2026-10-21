"""
Job postings scraper for school_id 1565 - West Virginia University Institute of Technology (US)
ATS platform: own website
Careers link: https://wvu.taleo.net/careersection/faculty/jobsearch.ftl?lang=en&portal=26100021550

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for West Virginia University Institute of Technology; nothing here affects any
other school's script.

Link check (ok): 17 posting-shaped links found.

NOTE: 2 schools list against this same URL, so this listing carries every one of their postings, not just this school's: West Virginia University.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1565_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1565_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
WVU's faculty Taleo section serves every campus; its search service is filtered by the City facet (Beckley).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1565
SCHOOL_NAME = 'West Virginia University Institute of Technology'
CAREERS_LINK = 'https://wvu.taleo.net/careersection/faculty/jobsearch.ftl?lang=en&portal=26100021550'
ATS_PLATFORM = 'own website'

CITY = '5800120139'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.taleo_rest_jobs('wvu.taleo.net', 'faculty', '26100021550', [CITY])


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
