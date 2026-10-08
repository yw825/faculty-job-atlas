"""
Job postings scraper for school_id 1602 - University of Winnipeg (Canada)
ATS platform: Avanti
Careers link: https://plus.avanti.ca/job-board/5da7a070-4efb-4f6e-b846-5d1e55cc2abe/abc8cefc-8900-4f89-a11a-169e8102b2be/view?LOCALE=en-CA&SEARCH=UWFA-RAS

CUSTOMIZED (confirmed live): this Avanti job board is a JS app where each
job row's title has no real href at all (role="link" on a <li>, JS click
handling only) -- but every row DOES expose its own job UUID directly in a
data-testid attribute ("public-jobs-job-<uuid>-id-text"), no click needed.
Confirmed live: clicking a row navigates to
".../job-board/<company-id>/<job-id>/view?..." -- the SAME URL shape as
CAREERS_LINK itself, just with that job's own UUID swapping in for the
second path segment -- so the real per-posting URLs can be built directly
from the data-testid UUIDs without clicking anything. Confirmed live: 6
unique UUIDs found, matching the page's own "Jobs (6)" count.

TUNED FIND_LINKS
Avanti job board, filtered to the faculty association (SEARCH=UWFA-RAS).
The list renders job cards with no hrefs; each card's id is in its
data-testid ("public-jobs-job-<uuid>-..."), and the posting URL is
job-board/<board>/<uuid>/view with the same filter.

Writes school_job_posts/school_id_1602_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1602_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1602
SCHOOL_NAME = 'University of Winnipeg'
CAREERS_LINK = 'https://plus.avanti.ca/job-board/5da7a070-4efb-4f6e-b846-5d1e55cc2abe/abc8cefc-8900-4f89-a11a-169e8102b2be/view?LOCALE=en-CA&SEARCH=UWFA-RAS'
ATS_PLATFORM = 'Avanti'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

JOB_TESTID_RE = re.compile(r'public-jobs-job-([0-9a-f-]{36})-id-text')


POSTING_RE = re.compile(r'^https://plus\.avanti\.ca/job-board/5da7a070-4efb-4f6e-b846-5d1e55cc2abe/(?!abc8cefc-8900-4f89-a11a-169e8102b2be)[0-9a-f-]{36}/view', re.I)


BOARD = 'https://plus.avanti.ca/job-board/5da7a070-4efb-4f6e-b846-5d1e55cc2abe'
JOB_ID_RE = re.compile(r'data-testid="public-jobs-job-([0-9a-f-]{36})-', re.I)


def find_links():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 8000)
    ids = list(dict.fromkeys(JOB_ID_RE.findall(html)))
    return [f'{BOARD}/{jid}/view?LOCALE=en-CA&SEARCH=UWFA-RAS' for jid in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
