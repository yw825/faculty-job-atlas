"""
Job postings scraper for school_id 1972 - The University of Texas Health Science Center at San Antonio (US)
ATS platform: Taleo
Careers link: https://uthscsa.referrals.selectminds.com/faculty

UT Health San Antonio's faculty SelectMinds board (search page lists all).

Writes school_job_posts/school_id_1972_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1972_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1972
SCHOOL_NAME = "The University of Texas Health Science Center at San Antonio"
CAREERS_LINK = 'https://uthscsa.referrals.selectminds.com/faculty'
ATS_PLATFORM = 'Taleo'

BOARD = 'https://uthscsa.referrals.selectminds.com/faculty/jobs/search'

POSTING_RE = re.compile(r'^https://uthscsa\.referrals\.selectminds\.com/faculty/jobs/[a-z0-9-]+-\d+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(BOARD, POSTING_RE, render=True, wait_ms=8000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
