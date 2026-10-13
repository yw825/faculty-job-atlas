"""
Job postings scraper for school_id 320 - University of Guam (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://uog.peopleadmin.com/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&855%5B%5D=1&commit=Search

University of Guam runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_320_job_posts.csv (school_id, post_link).
Checkpointed to school_id_320_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers link is a PeopleAdmin search with the audit's filters on it.
The board's Atom feed ignores them and returns every posting, so the
filtered search itself is paged.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 320
SCHOOL_NAME = 'University of Guam'
CAREERS_LINK = 'https://uog.peopleadmin.com/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&855%5B%5D=1&commit=Search'
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
