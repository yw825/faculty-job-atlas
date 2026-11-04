"""
Job postings scraper for school_id 495 - University of Kentucky
ATS platform: Workday (detected: workday)
Careers link: https://careers.uky.edu/careers/hr

University of Kentucky runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 121 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
workday school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_495_job_posts.csv (school_id, post_link).
Checkpointed to school_id_495_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers link is UK's careers gateway, which sends faculty and staff
applicants to its PeopleAdmin board, ukjobs.uky.edu (the audit's example is a
posting there).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 495
SCHOOL_NAME = 'University of Kentucky'
CAREERS_LINK = 'https://careers.uky.edu/careers/hr'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

BOARD = 'https://ukjobs.uky.edu/postings/search'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_peopleadmin_search(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
