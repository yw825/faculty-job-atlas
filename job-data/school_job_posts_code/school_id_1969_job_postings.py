"""
Job postings scraper for school_id 1969 - The University of Texas Southwestern Medical Center (US)
ATS platform: Taleo
Careers link: https://jobs.utsouthwestern.edu/job-search-results/?category[]=Faculty%20and%20Physicians

UT Southwestern career site, category Faculty and Physicians; 12 per page (&pg=N).

Writes school_job_posts/school_id_1969_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1969_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1969
SCHOOL_NAME = "The University of Texas Southwestern Medical Center"
CAREERS_LINK = 'https://jobs.utsouthwestern.edu/job-search-results/?category[]=Faculty%20and%20Physicians'
ATS_PLATFORM = 'Taleo'

POSTING_RE = re.compile(r'^https://jobs\.utsouthwestern\.edu/job/\d+/[a-z0-9-]+/$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_query_pages(CAREERS_LINK + '&pg={p}', POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
