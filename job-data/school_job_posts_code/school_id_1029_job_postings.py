"""
Job postings scraper for school_id 1029 - Wright State University-Lake Campus (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.wright.edu/postings/search

Wright State University-Lake Campus runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1029_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1029_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Wright State's one PeopleAdmin board (Faculty/Instructional category); this
campus's postings are those whose Department names the Lake Campus.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1029
SCHOOL_NAME = 'Wright State University-Lake Campus'
CAREERS_LINK = 'https://jobs.wright.edu/postings/search'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

BOARD = 'https://jobs.wright.edu/postings/search?query=&643%5B%5D=3&commit=Search'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_wright_state(BOARD, lake=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
