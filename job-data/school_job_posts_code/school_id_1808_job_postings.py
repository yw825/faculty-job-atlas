"""
Job postings scraper for school_id 1808 - Adelaide University (Australia)
ATS platform: own website
Careers link: https://jobs.adelaide.edu.au/jobs/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Adelaide University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1808_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1808_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
PageUp board paged by /jobs/search?page=N; pages are walked
until one adds nothing. Postings are /jobs/<slug>; menu and search links are
not kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1808
SCHOOL_NAME = 'Adelaide University'
CAREERS_LINK = 'https://jobs.adelaide.edu.au/jobs/search'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_query_pages('https://jobs.adelaide.edu.au/jobs/search?page={p}',
                                  re.compile(r'jobs\.adelaide\.edu\.au/jobs/(?!search)[a-z0-9-]+$'))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
