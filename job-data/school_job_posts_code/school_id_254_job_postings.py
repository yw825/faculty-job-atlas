"""
Job postings scraper for school_id 254 - University of Central Florida (US)
ATS platform: Workday (detected: workday)
Careers link: https://jobs.ucf.edu/jobs/search

University of Central Florida runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_254_job_posts.csv (school_id, post_link).
Checkpointed to school_id_254_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The board is paged by ?page=N (the plain page is an empty 202, so it is
rendered); pages are walked until one adds nothing and only postings are kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 254
SCHOOL_NAME = 'University of Central Florida'
CAREERS_LINK = 'https://jobs.ucf.edu/jobs/search'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [u.split('?')[0] for u in lib.scrape_query_pages('https://jobs.ucf.edu/jobs/search?page={p}',
                                                           re.compile(r'jobs\.ucf\.edu/jobs/(?!search)[a-z0-9-]+$'))]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
