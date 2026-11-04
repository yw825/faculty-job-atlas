"""
Job postings scraper for school_id 846 - University of New Hampshire-Durham (US)
ATS platform: Workday (detected: workday)
Careers link: https://usnh.wd5.myworkdayjobs.com/Careers?locations=1ec6efc49793100117073793de1e0000&workerSubType=b4f41dd8de101000c45c0fa670c90000&workerSubType=b4f41dd8de101000c45c0d3fc2a10001&workerSubType=b4f41dd8de101000c45c0e733dc30002

University of New Hampshire-Main Campus runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 3 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Keene State College, Plymouth State University.

Writes school_job_posts/school_id_846_job_posts.csv (school_id, post_link).
Checkpointed to school_id_846_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Workday board; the link carries the board's own filters (institution or
location, and faculty worker types / bargaining unit).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 846
SCHOOL_NAME = 'University of New Hampshire-Durham'
CAREERS_LINK = 'https://usnh.wd5.myworkdayjobs.com/Careers?locations=1ec6efc49793100117073793de1e0000&workerSubType=b4f41dd8de101000c45c0fa670c90000&workerSubType=b4f41dd8de101000c45c0d3fc2a10001&workerSubType=b4f41dd8de101000c45c0e733dc30002'
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
