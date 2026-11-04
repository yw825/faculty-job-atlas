"""
Job postings scraper for school_id 1626 - Trent University (Canada)
ATS platform: own website
Careers link: https://www.trentu.ca/humanresources/employment-opportunities/full-time-faculty-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Trent University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is /humanresources/careers/full-time-faculty/<slug>?<id>.

Writes school_job_posts/school_id_1626_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1626_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1626
SCHOOL_NAME = 'Trent University'
CAREERS_LINK = 'https://www.trentu.ca/humanresources/employment-opportunities/full-time-faculty-positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.trentu\.ca/humanresources/careers/full-time-faculty/[^/?#]+\?\d+$', re.I)


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
