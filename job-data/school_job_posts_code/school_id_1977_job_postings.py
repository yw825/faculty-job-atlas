"""
Job postings scraper for school_id 1977 - Washington State University-Tri-Cities (US)
ATS platform: Workday
Careers link: https://wsu.wd5.myworkdayjobs.com/WSU_Jobs?jobFamilyGroup=7a7d62448767019c28e399bff8053d45&locations=d013a30e9e950101ee161b3cabc30000

WSU Workday (WSU_Jobs), job family Faculty + campus location.

Writes school_job_posts/school_id_1977_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1977_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1977
SCHOOL_NAME = "Washington State University-Tri-Cities"
CAREERS_LINK = 'https://wsu.wd5.myworkdayjobs.com/WSU_Jobs?jobFamilyGroup=7a7d62448767019c28e399bff8053d45&locations=d013a30e9e950101ee161b3cabc30000'
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
