"""
Job postings scraper for school_id 1934 - Montana State University-Great Falls College (US)
ATS platform: PeopleAdmin
Careers link: https://jobs.gfcmsu.edu/postings/search?query=&query_position_type_id%5B%5D=2&commit=Search

Great Falls College MSU's PeopleAdmin search with its Faculty position type.

Writes school_job_posts/school_id_1934_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1934_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1934
SCHOOL_NAME = 'Montana State University-Great Falls College'
CAREERS_LINK = 'https://jobs.gfcmsu.edu/postings/search?query=&query_position_type_id%5B%5D=2&commit=Search'
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
