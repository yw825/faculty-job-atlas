"""
Job postings scraper for school_id 1655 - University of Regina (Canada)
ATS platform: own website
Careers link: https://urcareers.uregina.ca/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&435=&225=&1245%5B%5D=2&commit=Search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Regina; nothing here affects any
other school's script.

TUNED FIND_LINKS
PeopleAdmin search (faculty filter): each opening is /postings/<id>;
result pages (&page=N) are walked until one adds nothing.

Writes school_job_posts/school_id_1655_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1655_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1655
SCHOOL_NAME = 'University of Regina'
CAREERS_LINK = 'https://urcareers.uregina.ca/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&435=&225=&1245%5B%5D=2&commit=Search'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://urcareers\.uregina\.ca/postings/\d+$', re.I)


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
