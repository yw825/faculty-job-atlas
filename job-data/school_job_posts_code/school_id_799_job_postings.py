"""
Job postings scraper for school_id 799 - Mars Hill University (US)
ATS platform: own website
Careers link: https://jobs.appone.com/marshilluniversity

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Mars Hill University; nothing here affects any
other school's script.

Link check (review): 0 posting-shaped links found -- rendered no job-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_799_job_posts.csv (school_id, post_link).
Checkpointed to school_id_799_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Mars Hill's AppOne board; postings are apply.appone.com/job/<id>.
Mars Hill's AppOne board; the jobs come from the board's own public job-post
service (the page is an app).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 799
SCHOOL_NAME = 'Mars Hill University'
CAREERS_LINK = 'https://jobs.appone.com/marshilluniversity'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://apply\.appone\.com/job/[0-9a-f]+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    import json
    status, text = lib.fetch_static('https://jobs.appone.com/api/portal/v1/companyjobposts/marshilluniversity', timeout=40)
    if status != 200:
        raise RuntimeError(f'appone status={status}')
    return [j['jobPostUrl'] for j in json.loads(text).get('jobPosts') or []]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
