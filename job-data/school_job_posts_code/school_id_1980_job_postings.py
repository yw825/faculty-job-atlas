"""
Job postings scraper for school_id 1980 - Vermont State University-Lyndon (US)
ATS platform: Workday
Careers link: https://vsc.wd108.myworkdayjobs.com/VTSU?jobFamilyGroup=c6524e89e5a81000e34dd1c454830000&jobFamilyGroup=c6524e89e5a81000e34f3bc69de80000&jobFamilyGroup=c6524e89e5a81000e34edb0d7fdd0000&locations=c6524e89e5a81000e346082657f90000

Vermont State University Workday (VTSU), faculty job families + campus location.

Writes school_job_posts/school_id_1980_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1980_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1980
SCHOOL_NAME = "Vermont State University-Lyndon"
CAREERS_LINK = 'https://vsc.wd108.myworkdayjobs.com/VTSU?jobFamilyGroup=c6524e89e5a81000e34dd1c454830000&jobFamilyGroup=c6524e89e5a81000e34f3bc69de80000&jobFamilyGroup=c6524e89e5a81000e34edb0d7fdd0000&locations=c6524e89e5a81000e346082657f90000'
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
