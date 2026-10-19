"""
Job postings scraper for school_id 1128 - Lebanon Valley College (US)
ATS platform: own website
Careers link: https://www.lvc.edu/human-resources/employment/faculty-openings/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Lebanon Valley College; nothing here affects any
other school's script.

Link check (ok): 6 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1128_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1128_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers page sends applicants to this ADP Workforce Now board (whole board).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1128
SCHOOL_NAME = 'Lebanon Valley College'
CAREERS_LINK = 'https://www.lvc.edu/human-resources/employment/faculty-openings/'
ATS_PLATFORM = 'own website'

BOARD = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=c6864f58-380f-4d35-a085-a83ec5fb3f0b&ccId=19000101_000001&lang=en_US'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_adp(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
