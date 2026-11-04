"""
Job postings scraper for school_id 1609 - Memorial University of Newfoundland (Canada)
ATS platform: own website
Careers link: https://mun.ca/academic-careers/opportunities/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Memorial University of Newfoundland; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps: the Opportunities page links one page per faculty/school
(/academic-careers/opportunities/<unit>/), and each of those links its ads
as files, careers.mun.ca/<unit>/api/careers/file/<id>.

Writes school_job_posts/school_id_1609_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1609_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1609
SCHOOL_NAME = 'Memorial University of Newfoundland'
CAREERS_LINK = 'https://mun.ca/academic-careers/opportunities/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


HUB_RE = re.compile(r'^https://mun\.ca/academic-careers/opportunities/[^/?#]+/$', re.I)
POSTING_RE = re.compile(r'^https://careers\.mun\.ca/[^/]+/api/careers/file/\d+$', re.I)


def find_links():
    return lib.scrape_two_hop(CAREERS_LINK, HUB_RE, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
