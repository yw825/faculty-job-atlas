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


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    parsed = lib.urlsplit(CAREERS_LINK)
    company_id = parsed.path.strip('/').split('/')[1]
    ids, links = set(), []
    for el in soup.find_all(attrs={'data-testid': JOB_TESTID_RE}):
        m = JOB_TESTID_RE.search(el['data-testid'])
        job_id = m.group(1)
        if job_id not in ids:
            ids.add(job_id)
            links.append(f'{parsed.scheme}://{parsed.netloc}/job-board/{company_id}/{job_id}/view?{parsed.query}')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
