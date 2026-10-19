"""
Job postings scraper for school_id 985 - Paul Smiths College of Arts and Science (US)
ATS platform: own website
Careers link: https://www.paulsmiths.edu/careers/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Paul Smiths College of Arts and Science; nothing here affects any
other school's script.

Link check (ok): 13 posting-shaped links found -- rendered.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_985_job_posts.csv (school_id, post_link).
Checkpointed to school_id_985_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Each opening is /careers/?jobId=<id> on the careers page (a ClearCompany feed).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 985
SCHOOL_NAME = 'Paul Smiths College of Arts and Science'
CAREERS_LINK = 'https://www.paulsmiths.edu/careers/'
ATS_PLATFORM = 'own website'

DOC_RE = r'paulsmiths\.edu/careers/\?jobId=[0-9a-f-]+$'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [link for link, _text in lib.linked_documents(CAREERS_LINK, DOC_RE, render=True)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
