"""
Job postings scraper for school_id 1332 - Lincoln Memorial University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://careers.lmunet.edu/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&797%5B%5D=3&commit=Search

The careers link was https://www.peopleadmin.com/ -- the VENDOR's marketing
homepage rather than Lincoln Memorial's tenant, so the adapter asked
www.peopleadmin.com for an Atom feed and got a 404 on every run. The
university's own employment page links to careers.lmunet.edu, whose
/postings/all_jobs.atom answers with 146 entries.

Lincoln Memorial University runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1332_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1332_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
PeopleAdmin search; the link's own filters are kept.
The careers link leaves out the board's Adjunct and Faculty Part Time type; it is read too (full-time and adjunct faculty).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1332
SCHOOL_NAME = 'Lincoln Memorial University'
CAREERS_LINK = 'https://careers.lmunet.edu/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&797%5B%5D=3&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

BOARD = 'https://careers.lmunet.edu/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&797%5B%5D=3&commit=Search&797%5B%5D=4&797%5B%5D=5'

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
