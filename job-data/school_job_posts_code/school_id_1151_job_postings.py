"""
Job postings scraper for school_id 1151 - Gannon University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://gannon.peopleadmin.com/postings/search?query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search

Gannon University runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1151_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1151_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
PeopleAdmin search; the link's own filters are kept (lib.scrape_peopleadmin_search).
The careers link is the Faculty position type; the board's Adjunct type is read too
(full-time and adjunct faculty).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1151
SCHOOL_NAME = 'Gannon University'
CAREERS_LINK = 'https://gannon.peopleadmin.com/postings/search?query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

BOARD = 'https://gannon.peopleadmin.com/postings/search?query=&query_position_type_id%5B%5D=3&query_position_type_id%5B%5D=6&commit=Search'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_peopleadmin_search(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
