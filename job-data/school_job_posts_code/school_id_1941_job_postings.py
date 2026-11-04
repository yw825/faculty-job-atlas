"""
Job postings scraper for school_id 1941 - Fayetteville State University (US)
ATS platform: PeopleAdmin
Careers link: https://jobs.uncfsu.edu/postings/search?query=&612%5B%5D=12&commit=Search

The university's PeopleAdmin search with its own faculty filter; the search
itself is paged so the filter is kept (the board's Atom feed ignores it).

Writes school_job_posts/school_id_1941_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1941_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1941
SCHOOL_NAME = 'Fayetteville State University'
CAREERS_LINK = 'https://jobs.uncfsu.edu/postings/search?query=&612%5B%5D=12&commit=Search'
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
