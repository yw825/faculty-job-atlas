"""
Job postings scraper for school_id 1967 - Texas A & M University-Galveston (US)
ATS platform: own website
Careers link: https://faculty.tamu.edu/

Texas A&M's faculty job board (faculty.tamu.edu), postings located in Galveston.

Writes school_job_posts/school_id_1967_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1967_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1967
SCHOOL_NAME = "Texas A & M University-Galveston"
CAREERS_LINK = 'https://faculty.tamu.edu/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.tamu_faculty_jobs(include=r'(?i)galveston')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
