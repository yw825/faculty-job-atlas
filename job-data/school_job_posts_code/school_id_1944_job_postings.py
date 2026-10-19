"""
Job postings scraper for school_id 1944 - University of Nevada-Reno at Lake Tahoe (US)
ATS platform: Workday (NSHE)
Careers link: https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=2f340f89d727010108e3cdda09720000&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313

UNR's NSHE Workday site with its Lake Tahoe location and faculty categories.

Writes school_job_posts/school_id_1944_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1944_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1944
SCHOOL_NAME = "University of Nevada-Reno at Lake Tahoe"
CAREERS_LINK = 'https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=2f340f89d727010108e3cdda09720000&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313'
ATS_PLATFORM = 'Workday (NSHE)'

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
