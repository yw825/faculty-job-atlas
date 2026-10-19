"""
Job postings scraper for school_id 1964 - Pennsylvania State University-College of Medicine (US)
ATS platform: Workday
Careers link: https://psu.wd1.myworkdayjobs.com/PSU_Academic?locations=5734019731720183ab8270b2e14a6663&locations=ac1efd63d810018e310ca031c701f81b

Workday board; the link's facets (job family / location) are kept.

Writes school_job_posts/school_id_1964_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1964_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1964
SCHOOL_NAME = "Pennsylvania State University-College of Medicine"
CAREERS_LINK = 'https://psu.wd1.myworkdayjobs.com/PSU_Academic?locations=5734019731720183ab8270b2e14a6663&locations=ac1efd63d810018e310ca031c701f81b'
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
