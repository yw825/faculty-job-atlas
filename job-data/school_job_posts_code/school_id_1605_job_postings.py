"""
Job postings scraper for school_id 1605 - Yorkville University (Canada)
ATS platform: own website
Careers link: https://www.yorkvilleu.ca/job-postings/

CUSTOMIZED (confirmed live): the postings on this page are embedded via an
<iframe> pointing at a separate JazzHR-hosted board
(yorkvilleuniversity.applytojob.com/apply/jobs/) -- fetch_rendered only
ever returns the TOP-level document (see job_postings_lib.fetch_rendered),
so the embedded postings were invisible no matter what filter was applied
to the parent page. Fetching that iframe URL directly instead finds real
"/apply/jobs/details/<id>" links; the one exception is a "Talent Community"
entry, a generic mailing-list signup rather than a specific opening,
excluded explicitly.

TUNED FIND_LINKS
The #job-listings section of the job-postings page is an iframe of the
JazzHR board, yorkvilleuniversity.applytojob.com/apply/jobs/, which is read
directly; each opening is .../apply/jobs/details/<id> (stored without the
trailing "?&").

Writes school_job_posts/school_id_1605_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1605_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1605
SCHOOL_NAME = 'Yorkville University'
CAREERS_LINK = 'https://www.yorkvilleu.ca/job-postings/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

JOB_BOARD_URL = 'https://yorkvilleuniversity.applytojob.com/apply/jobs/'
DETAILS_RE = re.compile(r'/jobs/details/')


POSTING_RE = re.compile(r'^https://yorkvilleuniversity\.applytojob\.com/apply/jobs/details/[A-Za-z0-9]+', re.I)


BOARD = 'https://yorkvilleuniversity.applytojob.com/apply/jobs/'
POSTING_RE = re.compile(r'^https://yorkvilleuniversity\.applytojob\.com/apply/jobs/details/[A-Za-z0-9]+', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(BOARD, POSTING_RE):
        url = POSTING_RE.match(url).group(0)
        if url not in links:
            links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
