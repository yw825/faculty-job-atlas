"""
Job postings scraper for school_id 1624 - Carleton University (Canada)
ATS platform: own website
Careers link: https://carleton.ca/deputyprovost/jobs/academics/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Carleton University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is a dated post, /deputyprovost/<year>/<slug>/, listed on
the Current Academic Job Postings page.

Writes school_job_posts/school_id_1624_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1624_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1624
SCHOOL_NAME = 'Carleton University'
CAREERS_LINK = 'https://carleton.ca/deputyprovost/jobs/academics/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://carleton\.ca/deputyprovost/20\d\d/[^/?#]+/?$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
