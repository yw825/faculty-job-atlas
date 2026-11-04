"""
Job postings scraper for school_id 205 - Georgetown University (US)
ATS platform: Workday (detected: workday)
Careers link: https://apply.interfolio.com/11780/positions

Georgetown University runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_205_job_posts.csv (school_id, post_link).
Checkpointed to school_id_205_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Georgetown's Workday site (the audit's link) is its administrative board;
faculty and postdoc openings are on its Interfolio board 11780. Both are read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 205
SCHOOL_NAME = 'Georgetown University'
CAREERS_LINK = 'https://apply.interfolio.com/11780/positions'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

STAFF_BOARD = 'https://georgetown.wd1.myworkdayjobs.com/Georgetown_Admin_Careers'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return list(dict.fromkeys(lib.scrape_interfolio(CAREERS_LINK) + lib.PLATFORM_ADAPTERS['workday'](STAFF_BOARD, SCHOOL_NAME)))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
