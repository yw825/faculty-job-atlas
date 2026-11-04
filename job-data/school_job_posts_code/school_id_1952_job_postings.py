"""
Job postings scraper for school_id 1952 - SUNY-Downstate Health Sciences University (US)
ATS platform: PageUp
Careers link: https://jobs.downstate.edu/en-us/listing/

Downstate's PageUp board, asked for 500 at a time.

Writes school_job_posts/school_id_1952_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1952_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1952
SCHOOL_NAME = "SUNY-Downstate Health Sciences University"
CAREERS_LINK = 'https://jobs.downstate.edu/en-us/listing/'
ATS_PLATFORM = 'PageUp'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_pageup_listing(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
