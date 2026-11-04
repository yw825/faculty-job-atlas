"""
Job postings scraper for school_id 1853 - City University of Macau (Macau)
ATS platform: own website
Careers link: https://hro.cityu.edu.mo/en/category/job-application/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for City University of Macau; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1853_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1853_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
City University of Macau's job-application category is a WordPress archive,
10 posts per page (/page/2/, /page/3/); postings are dated posts
/en/YYYY/MM/DD/<slug>/.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1853
SCHOOL_NAME = 'City University of Macau'
CAREERS_LINK = 'https://hro.cityu.edu.mo/en/category/job-application/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for page in range(1, 30):
        url = CAREERS_LINK if page == 1 else f'{CAREERS_LINK.rstrip("/")}/page/{page}/'
        status, html = lib.fetch_static(url, timeout=40)
        if status != 200:
            if page == 1:
                raise RuntimeError(f'category status={status}')
            break
        new = [u for u in re.findall(r'href="(https://hro\.cityu\.edu\.mo/en/20\d\d/\d\d/\d\d/[a-z0-9-]+/)"', html) if u not in links]
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
