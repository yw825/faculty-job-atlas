"""
Job postings scraper for school_id 648 - Cleary University
ATS platform: Paycor Recruiting (detected: paycor)
Careers link: https://recruitingbypaycor.com/career/CareerHome.action?clientId=8a7883d096d0d55a019731393c7f56d9

Cleary University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_paycor adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 16 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
paycor school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_648_job_posts.csv (school_id, post_link).
Checkpointed to school_id_648_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 648
SCHOOL_NAME = 'Cleary University'
CAREERS_LINK = 'https://recruitingbypaycor.com/career/CareerHome.action?clientId=8a7883d096d0d55a019731393c7f56d9'
ATS_PLATFORM = 'Paycor Recruiting'
PLATFORM = 'paycor'

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
