"""
Job postings scraper for school_id 1935 - University of North Carolina-School of the Arts (US)
ATS platform: PeopleAdmin
Careers link: https://employment.uncsa.edu/postings/search?query=&query_position_type_id%5B%5D=3&commit=Search

UNCSA's PeopleAdmin search with its EHRA Faculty position type.

Writes school_job_posts/school_id_1935_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1935_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1935
SCHOOL_NAME = 'University of North Carolina-School of the Arts'
CAREERS_LINK = 'https://employment.uncsa.edu/postings/search?query=&query_position_type_id%5B%5D=3&commit=Search'
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
