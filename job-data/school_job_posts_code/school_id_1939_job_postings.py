"""
Job postings scraper for school_id 1939 - Fairleigh Dickinson University-Vancouver Campus (US)
ATS platform: PeopleAdmin
Careers link: https://jobs.fdu.edu/postings/search

FDU's one PeopleAdmin board has no campus filter; postings whose "Campus:"
row names Vancouver are kept.

Writes school_job_posts/school_id_1939_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1939_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1939
SCHOOL_NAME = 'Fairleigh Dickinson University-Vancouver Campus'
CAREERS_LINK = 'https://jobs.fdu.edu/postings/search'
ATS_PLATFORM = 'PeopleAdmin'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_fdu_campus('Vancouver')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
