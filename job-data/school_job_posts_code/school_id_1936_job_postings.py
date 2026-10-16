"""
Job postings scraper for school_id 1936 - University of Nebraska-Medical Center (US)
ATS platform: PeopleAdmin
Careers link: https://unmc.peopleadmin.com/postings/search?query=&996%5B%5D=14&996%5B%5D=11&commit=Search

UNMC's PeopleAdmin search with its Faculty and Research - Academic posting
categories.

Writes school_job_posts/school_id_1936_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1936_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1936
SCHOOL_NAME = 'University of Nebraska-Medical Center'
CAREERS_LINK = 'https://unmc.peopleadmin.com/postings/search?query=&996%5B%5D=14&996%5B%5D=11&commit=Search'
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
