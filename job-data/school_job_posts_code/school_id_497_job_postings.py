"""
Job postings scraper for school_id 497 - Spalding University
ATS platform: Paycom (detected: paycom)
Careers link: https://spalding.edu/careers/

Spalding University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_paycom adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 13 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
paycom school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_497_job_posts.csv (school_id, post_link).
Checkpointed to school_id_497_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers page embeds the university's Paycom board (the audit's example
is a posting there); the board is read directly.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 497
SCHOOL_NAME = 'Spalding University'
CAREERS_LINK = 'https://spalding.edu/careers/'
ATS_PLATFORM = 'Paycom'
PLATFORM = 'paycom'

BOARD = 'https://www.paycomonline.net/v4/ats/web.php/portal/A99CE46A67143A8F77A8C7BDEA7155DA/career-page'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [row[0] for row in lib.paycom_previews(BOARD)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
