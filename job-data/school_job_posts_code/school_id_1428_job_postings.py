"""
Job postings scraper for school_id 1428 - Trinity University (US)
ATS platform: Workday
Careers link: https://trinity.wd1.myworkdayjobs.com/Trinity_University

Trinity was configured as an "own website" school pointed at
https://trinity.edu/hr/careers. That page is an HR landing page: it carries
no postings at all, so the generic link filter returned 4 links -- the
faculty directory, a "connect with faculty expertise" page and similar --
and every real opening was missed, including the Assistant Professor of
Business Analytics (JR101582) that a user found by hand on 2026-09-16.

The real board is the Workday tenant below, which answers the standard
Workday jobs API with 25 open positions. Workday is already a supported
platform here, so this school now just calls the shared adapter.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1428
SCHOOL_NAME = 'Trinity University'
CAREERS_LINK = 'https://trinity.wd1.myworkdayjobs.com/Trinity_University'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
