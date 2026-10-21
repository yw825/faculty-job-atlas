"""
Job postings scraper for school_id 1970 - The University of Texas Medical Branch (US)
ATS platform: Taleo
Careers link: https://aa083.referrals.selectminds.com/page/faculty-physicians-79

UTMB's Faculty & Physicians page on its Taleo/SelectMinds board.

Writes school_job_posts/school_id_1970_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1970_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1970
SCHOOL_NAME = "The University of Texas Medical Branch"
CAREERS_LINK = 'https://aa083.referrals.selectminds.com/page/faculty-physicians-79'
ATS_PLATFORM = 'Taleo'

POSTING_RE = re.compile(r'^https://aa083\.referrals\.selectminds\.com/jobs/[a-z0-9-]+-\d+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True, wait_ms=8000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
