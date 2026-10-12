"""
Job postings scraper for school_id 1768 - University of Glasgow (United Kingdom)
ATS platform: own website
Careers link: https://www.jobs.gla.ac.uk/jobs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Glasgow; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1768_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1768_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Glasgow's board shows 20 jobs per page (/jobs?page=N); the old scraper read
page 1 and kept category, apply and save links. Postings are /job/<slug>-<id>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1768
SCHOOL_NAME = 'University of Glasgow'
CAREERS_LINK = 'https://www.jobs.gla.ac.uk/jobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for page in range(1, 60):
        status, html = lib.fetch_static(f'https://www.jobs.gla.ac.uk/jobs?page={page}', timeout=40)
        if status != 200:
            if page == 1:
                raise RuntimeError(f'jobs status={status}')
            break
        new = [f'https://www.jobs.gla.ac.uk/job/{slug}' for slug in re.findall(r'href="[^"]*/job/([a-z0-9-]+-\d+)(?:\?[^"]*)?"', html)
               if f'https://www.jobs.gla.ac.uk/job/{slug}' not in links]
        new = list(dict.fromkeys(new))
        if not new:
            break
        links += new
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
