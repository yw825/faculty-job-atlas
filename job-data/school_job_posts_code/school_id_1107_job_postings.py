"""
Job postings scraper for school_id 1107 - Oregon State University-Corvallis (US)
ATS platform: Workday (detected: workday)
Careers link: https://oregonstate.wd501.myworkdayjobs.com/OSU_Careers_Site?Appointment_Type=d4ebbf013baa1000e7b9d02b288c0000

Oregon State University runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 2 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Oregon State University-Cascades Campus.

Writes school_job_posts/school_id_1107_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1107_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Oregon State's Workday board, Appointment Type "JFG: Academic"; postings located in
Bend belong to the Cascades row (1106).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1107
SCHOOL_NAME = "Oregon State University-Corvallis"
CAREERS_LINK = 'https://oregonstate.wd501.myworkdayjobs.com/OSU_Careers_Site?Appointment_Type=d4ebbf013baa1000e7b9d02b288c0000'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [u for u in lib.PLATFORM_ADAPTERS['workday'](CAREERS_LINK, SCHOOL_NAME) if '/job/Bend/' not in u]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
