"""
Job postings scraper for school_id 1515 - Washington State University-Pullman (US)
ATS platform: Workday (detected: workday)
Careers link: https://wsu.wd5.myworkdayjobs.com/WSU_Jobs?jobFamilyGroup=7a7d62448767019c28e399bff8053d45&locations=d013a30e9e950101ed94432b2c1f0000

Washington State University runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1515_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1515_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Workday site; the link's facets (job family / campus location) are kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1515
SCHOOL_NAME = "Washington State University-Pullman"
CAREERS_LINK = 'https://wsu.wd5.myworkdayjobs.com/WSU_Jobs?jobFamilyGroup=7a7d62448767019c28e399bff8053d45&locations=d013a30e9e950101ed94432b2c1f0000'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

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
