"""
Job postings scraper for school_id 1953 - SUNY-Upstate Medical University (US)
ATS platform: PageUp
Careers link: https://careers.upstate.edu/

careers.upstate.edu sends applicants to Upstate's PageUp board (872).

Writes school_job_posts/school_id_1953_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1953_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1953
SCHOOL_NAME = "SUNY-Upstate Medical University"
CAREERS_LINK = 'https://careers.upstate.edu/'
ATS_PLATFORM = 'PageUp'

BOARD = 'https://careers.pageuppeople.com/872/cw/en-us/listing/'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_pageup_listing(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
