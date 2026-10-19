"""
Job postings scraper for school_id 1949 - CUNY-School of Medicine (US)
ATS platform: cuny.jobs
Careers link: https://cuny.jobs/campus/cuny-school-of-medicine/job-category/faculty/jobs/

cuny.jobs campus + faculty category, read from its RSS feed in a normal Chrome
window (the site has an AWS bot check).

Writes school_job_posts/school_id_1949_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1949_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1949
SCHOOL_NAME = "CUNY-School of Medicine"
CAREERS_LINK = 'https://cuny.jobs/campus/cuny-school-of-medicine/job-category/faculty/jobs/'
ATS_PLATFORM = 'cuny.jobs'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_cuny(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
