"""
Job postings scraper for school_id 455 - Purdue University-West Lafayette (US)
ATS platform: own website
Careers link: https://careers.purdue.edu/go/West-Lafayette-Faculty/7721600/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Purdue University-West Lafayette; nothing here affects any
other school's script.

Link check (ok): 9 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_455_job_posts.csv (school_id, post_link).
Checkpointed to school_id_455_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Purdue's careers site has a section per campus; this is the West Lafayette (incl. Indianapolis)
faculty category, read from the site's own job service.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 455
SCHOOL_NAME = 'Purdue University-West Lafayette'
CAREERS_LINK = 'https://careers.purdue.edu/go/West-Lafayette-Faculty/7721600/'
ATS_PLATFORM = 'own website'

BRAND = ''
CATEGORY = 7721600

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = lib.scrape_sf_rmk('https://careers.purdue.edu', brand=BRAND, category_id=CATEGORY, locale='en_US')
    return [u.replace('https://careers.purdue.edu/job/', f'https://careers.purdue.edu/{BRAND}/job/') if BRAND else u for u in links]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
