"""
Job postings scraper for school_id 638 - Kettering University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.kettering.edu/postings/search

Kettering University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here.

The careers link was www.kettering.edu/co-op-career-design -- the page about
Kettering's co-op programme for STUDENTS looking for placements, not the
university's own hiring. It is job-shaped enough to pass a generic filter,
which is why the school recorded three links from it and no real postings.
Kettering's board is jobs.kettering.edu, whose Atom feed lists 12.

Writes school_job_posts/school_id_638_job_posts.csv (school_id, post_link).
Checkpointed to school_id_638_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers link is a PeopleAdmin search; the search itself is paged so any
filter on the link (position type) is kept -- the board's Atom feed ignores
filters.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 638
SCHOOL_NAME = 'Kettering University'
CAREERS_LINK = 'https://jobs.kettering.edu/postings/search'
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
