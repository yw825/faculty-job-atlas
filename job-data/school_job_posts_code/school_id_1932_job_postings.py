"""
Job postings scraper for school_id 1932 - Missouri State University-West Plains (US)
ATS platform: PeopleAdmin
Careers link: https://jobs.missouristate.edu/postings/search?query=&query_position_type_id%5B%5D=2&query_position_type_id%5B%5D=5&513%5B%5D=3&commit=Search

Missouri State's PeopleAdmin search with its own campus (West Plains) and
Full-Time / Adjunct Faculty filters.

Writes school_job_posts/school_id_1932_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1932_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1932
SCHOOL_NAME = 'Missouri State University-West Plains'
CAREERS_LINK = 'https://jobs.missouristate.edu/postings/search?query=&query_position_type_id%5B%5D=2&query_position_type_id%5B%5D=5&513%5B%5D=3&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_peopleadmin_search(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
