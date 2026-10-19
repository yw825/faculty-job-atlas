"""
Job postings scraper for school_id 1051 - Miami University-Hamilton (US)
ATS platform: Workday (detected: workday)
Careers link: https://miamioh.wd5.myworkdayjobs.com/miamioh-faculty?locations=c79d26910af9100520aac2b74d840000

Miami University-Hamilton runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 3 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Miami University-Middletown, Miami University-Oxford.

Writes school_job_posts/school_id_1051_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1051_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Workday board; the link carries the board's own filters (site, job category,
location).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1051
SCHOOL_NAME = 'Miami University-Hamilton'
CAREERS_LINK = 'https://miamioh.wd5.myworkdayjobs.com/miamioh-faculty?locations=c79d26910af9100520aac2b74d840000'
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
