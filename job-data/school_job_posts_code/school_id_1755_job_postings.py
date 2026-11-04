"""
Job postings scraper for school_id 1755 - University of St. Gallen (Switzerland)
ATS platform: own website
Careers link: https://www.unisg.ch/en/university/working-at-hsg/jobs/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of St. Gallen; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1755_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1755_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
HSG's jobs page hands off to jobs.unisg.ch (postings
/offene-stellen/<slug>/<uuid>, the audit's example; a plain request works,
a browser gets redirected back). Professorships are on a separate faculty
recruiting site linked from "Open Faculty Positions"
(facultyrecruiting.unisg.ch/positiondetails/<id>); both are read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1755
SCHOOL_NAME = 'University of St. Gallen'
CAREERS_LINK = 'https://www.unisg.ch/en/university/working-at-hsg/jobs/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static('https://jobs.unisg.ch/?sprCd=en', timeout=40)
    if status != 200:
        raise RuntimeError(f'jobs.unisg.ch status={status}')
    links = ['https://jobs.unisg.ch' + p for p in dict.fromkeys(re.findall(r'/offene-stellen/[a-z0-9-]+/[0-9a-f-]{36}', html))]
    try:
        faculty = lib._fetch_rendered_retry('https://www.unisg.ch/en/research/faculty/open-faculty-positions/', 5000)
        links += list(dict.fromkeys(re.findall(r'https://facultyrecruiting\.unisg\.ch/positiondetails/\d+', faculty)))
    except RuntimeError:
        pass
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
