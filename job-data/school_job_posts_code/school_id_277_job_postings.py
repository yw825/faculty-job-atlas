"""
Job postings scraper for school_id 277 - Georgia State University
ATS platform: PeopleAdmin
Careers link: https://facultycareers.gsu.edu/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search

gsu.taleo.net answers with an SSO redirect stub (saml20authnrequestservlet),
not a job board, so this school sat at zero. Its faculty postings are on a
PeopleAdmin board, which serves 30 openings over plain HTTP.

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

SCHOOL_ID = 277
SCHOOL_NAME = 'Georgia State University'
CAREERS_LINK = 'https://facultycareers.gsu.edu/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search'
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
