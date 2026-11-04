"""
Job postings scraper for school_id 1937 - University of New Hampshire-Franklin Pierce School of Law (US)
ATS platform: Workday (USNH)
Careers link: https://usnh.wd5.myworkdayjobs.com/Careers?locations=1ec6efc497931001170554505e2d0000&workerSubType=b4f41dd8de101000c45c0fa670c90000&workerSubType=b4f41dd8de101000c45c0d3fc2a10001&workerSubType=b4f41dd8de101000c45c0e733dc30002

The University System of New Hampshire's Workday board with its own location
(Franklin Pierce School of Law) and faculty worker-type filters.

Writes school_job_posts/school_id_1937_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1937_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1937
SCHOOL_NAME = 'University of New Hampshire-Franklin Pierce School of Law'
CAREERS_LINK = 'https://usnh.wd5.myworkdayjobs.com/Careers?locations=1ec6efc497931001170554505e2d0000&workerSubType=b4f41dd8de101000c45c0fa670c90000&workerSubType=b4f41dd8de101000c45c0d3fc2a10001&workerSubType=b4f41dd8de101000c45c0e733dc30002'
ATS_PLATFORM = 'Workday (USNH)'

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
