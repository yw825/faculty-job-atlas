"""
Job postings scraper for school_id 526 - Louisiana Tech University (US)
ATS platform: Workday (detected: workday)
Careers link: https://www.latech.edu/business/about/employment-opportunities.php

Louisiana Tech University runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_526_job_posts.csv (school_id, post_link).
Checkpointed to school_id_526_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The audit's link is the College of Business employment page, which lists a
few openings; they and the audit's example are postings on Louisiana Tech's
Workday board, which is read in full.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 526
SCHOOL_NAME = 'Louisiana Tech University'
CAREERS_LINK = 'https://www.latech.edu/business/about/employment-opportunities.php'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

BOARD = 'https://ulsltu.wd503.myworkdayjobs.com/LATECHCareers'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.PLATFORM_ADAPTERS['workday'](BOARD, SCHOOL_NAME)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
