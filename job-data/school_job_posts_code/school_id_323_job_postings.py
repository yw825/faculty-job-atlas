"""
Job postings scraper for school_id 323 - Hawaii Pacific University (US)
ATS platform: own website
Careers link: https://www.schooljobs.com/careers/hpu?jobType[0]=Faculty%20-%20Regular%20Full%20Time&jobType[1]=Faculty%20-%20Adjunct%20Faculty&jobType[2]=Faculty%20-%20Temporary%20Full%20Time&jobType[3]=Faculty%20-%20Mentor%20Teacher&sort=PositionTitle%7CAscending

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Hawaii Pacific University; nothing here affects any
other school's script.

Link check (ok): 12 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_323_job_posts.csv (school_id, post_link).
Checkpointed to school_id_323_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
HPU's NEOGOV board only filters on a job type's full name, so the old
?jobType[0]=Faculty link showed 0 jobs. Faculty postings are the rows whose
job type starts with "Faculty" (Regular Full Time, Adjunct Faculty, ...).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 323
SCHOOL_NAME = 'Hawaii Pacific University'
CAREERS_LINK = 'https://www.schooljobs.com/careers/hpu?jobType[0]=Faculty%20-%20Regular%20Full%20Time&jobType[1]=Faculty%20-%20Adjunct%20Faculty&jobType[2]=Faculty%20-%20Temporary%20Full%20Time&jobType[3]=Faculty%20-%20Mentor%20Teacher&sort=PositionTitle%7CAscending'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


PLATFORM = 'schooljobs'


def find_links():
    return [url for url, _title, _loc, job_type, _dept in lib.neogov_rows('hpu') if job_type.startswith('Faculty')]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
