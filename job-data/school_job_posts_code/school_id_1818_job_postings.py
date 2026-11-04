"""
Job postings scraper for school_id 1818 - University of Notre Dame Australia (Australia)
ATS platform: own website
Careers link: https://search.nd.edu.au/s/search.html?collection=und~sp-jobs&profile=jobs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Notre Dame Australia; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1818_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1818_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Notre Dame's job search (Funnelback) shows 20 results per page
(start_rank=1,21,41,...) behind a Cloudflare check that a rendered load
passes; postings are .../job-details/_nocache?jobid=<id>. Facet links
(department, category, type) are not kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1818
SCHOOL_NAME = 'University of Notre Dame Australia'
CAREERS_LINK = 'https://search.nd.edu.au/s/search.html?collection=und~sp-jobs&profile=jobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    ids = []
    for start in range(1, 2000, 20):
        html = lib._fetch_rendered_retry(f'{CAREERS_LINK}&start_rank={start}', 5000)
        new = [i for i in dict.fromkeys(re.findall(r'job-details/_nocache\?jobid=([A-Za-z0-9_-]+)', html)) if i not in ids]
        if not new:
            break
        ids += new
    return ['https://www.notredame.edu.au/about-us/jobs-at-unda/employment-opportunities/job-details/_nocache?jobid=' + i for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
