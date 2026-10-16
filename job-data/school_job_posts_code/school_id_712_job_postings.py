"""
Job postings scraper for school_id 712 - Lincoln University (US)
ATS platform: ADP Workforce Now
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=6105d53b-aeb8-4656-a07d-2743bd4a2423&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter

Lincoln University's ADP board (the audit's corrected link); the HR
employment page links it.

Writes school_job_posts/school_id_712_job_posts.csv (school_id, post_link).
Checkpointed to school_id_712_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 712
SCHOOL_NAME = 'Lincoln University'
CAREERS_LINK = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=6105d53b-aeb8-4656-a07d-2743bd4a2423&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter'
ATS_PLATFORM = 'ADP Workforce Now'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.PLATFORM_ADAPTERS['adp'](CAREERS_LINK, SCHOOL_NAME)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
