"""
Job postings scraper for school_id 1928 - University of Maryland-Eastern Shore (US)
ATS platform: Workday (USM)
Careers link: https://umd.wd1.myworkdayjobs.com/UMES?workerSubType=87e92a4cca141000c7996897710c0000&workerSubType=87e92a4cca141000c79966b87c490001

UMES's site on the University System of Maryland Workday tenant, with the
board's own Faculty worker-type filters selected.

Writes school_job_posts/school_id_1928_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1928_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1928
SCHOOL_NAME = 'University of Maryland-Eastern Shore'
CAREERS_LINK = 'https://umd.wd1.myworkdayjobs.com/UMES?workerSubType=87e92a4cca141000c7996897710c0000&workerSubType=87e92a4cca141000c79966b87c490001'
ATS_PLATFORM = 'Workday (USM)'

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
