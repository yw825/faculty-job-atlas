"""
Job postings scraper for school_id 1268 - Brown University (US)
ATS platform: Workday (detected: workday)
Careers link: https://apply.interfolio.com/10128/positions

Brown University runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1268_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1268_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Brown's faculty openings as listed by HERC (the audit's link).
Brown's faculty searches run on Interfolio (board 10128); the audit link (HERC) now answers with a robot check.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1268
SCHOOL_NAME = 'Brown University'
CAREERS_LINK = 'https://apply.interfolio.com/10128/positions'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

POSTING_RE = re.compile(r'^https://main\.hercjobs\.org/jobs/\d+/[a-z0-9-]+')

BOARD = 'https://apply.interfolio.com/10128/positions'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_interfolio(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
