"""
Job postings scraper for school_id 1959 - Oklahoma State University-Tulsa (US)
ATS platform: own website
Careers link: https://jobs.okstate.edu/jobs/search/search-page-oklahoma-state?page=1&employment_type_uids%5B%5D=5c5da7ec2907fcbb8822ceda56aa53d0&employment_type_uids%5B%5D=369d5b24d91990b57f28e9ebbee41ffa&dropdown_field_2_uids%5B%5D=ebb62c9f15723dea2dd23f9d21d829bf

OSU system board (jobs.okstate.edu): the link's employment-type and Posting Campus
filters are kept; pages walked.

Writes school_job_posts/school_id_1959_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1959_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1959
SCHOOL_NAME = "Oklahoma State University-Tulsa"
CAREERS_LINK = 'https://jobs.okstate.edu/jobs/search/search-page-oklahoma-state?page=1&employment_type_uids%5B%5D=5c5da7ec2907fcbb8822ceda56aa53d0&employment_type_uids%5B%5D=369d5b24d91990b57f28e9ebbee41ffa&dropdown_field_2_uids%5B%5D=ebb62c9f15723dea2dd23f9d21d829bf'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://jobs\.okstate\.edu/jobs/(?!search)[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
