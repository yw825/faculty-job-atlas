"""
Job postings scraper for school_id 1927 - University of Maryland-Baltimore (US)
ATS platform: Oracle Cloud HCM
Careers link: https://efzv.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1013

UMB's Oracle Recruiting board, read through its public REST service.

Writes school_job_posts/school_id_1927_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1927_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1927
SCHOOL_NAME = 'University of Maryland-Baltimore'
CAREERS_LINK = 'https://efzv.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1013'
ATS_PLATFORM = 'Oracle Cloud HCM'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_oracle_link(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
