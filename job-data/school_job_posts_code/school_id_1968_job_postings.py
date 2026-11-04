"""
Job postings scraper for school_id 1968 - Prairie View A & M University (US)
ATS platform: Workday
Careers link: https://tamus.wd1.myworkdayjobs.com/PVAMU_External?workerSubType=0e1cd8ed3502012ddf607157e74b7d04

Texas A&M System Workday site (PVAMU_External), worker sub-type Faculty.

Writes school_job_posts/school_id_1968_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1968_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1968
SCHOOL_NAME = "Prairie View A & M University"
CAREERS_LINK = 'https://tamus.wd1.myworkdayjobs.com/PVAMU_External?workerSubType=0e1cd8ed3502012ddf607157e74b7d04'
ATS_PLATFORM = 'Workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.PLATFORM_ADAPTERS['workday'](CAREERS_LINK, SCHOOL_NAME)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
