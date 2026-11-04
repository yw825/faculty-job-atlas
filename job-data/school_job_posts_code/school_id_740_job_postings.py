"""
Job postings scraper for school_id 740 - Missouri State University-Springfield (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.missouristate.edu/postings/search?query=&query_position_type_id%5B%5D=2&query_position_type_id%5B%5D=5&513%5B%5D=1&513%5B%5D=2&commit=Search

Missouri State University-Springfield runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_740_job_posts.csv (school_id, post_link).
Checkpointed to school_id_740_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers link is a PeopleAdmin search; the search itself is paged so the
link's own filters (position type, campus) are kept -- the board's Atom
feed ignores filters.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 740
SCHOOL_NAME = 'Missouri State University-Springfield'
CAREERS_LINK = 'https://jobs.missouristate.edu/postings/search?query=&query_position_type_id%5B%5D=2&query_position_type_id%5B%5D=5&513%5B%5D=1&513%5B%5D=2&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

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
