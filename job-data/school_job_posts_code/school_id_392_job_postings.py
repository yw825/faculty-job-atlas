"""
Job postings scraper for school_id 392 - Knox College
ATS platform: ADP Workforce Now (detected: adp)
Careers link: https://www.knox.edu/employment-at-knox/faculty

Knox College runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 14 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
adp school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_392_job_posts.csv (school_id, post_link).
Checkpointed to school_id_392_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The faculty page links each opening as a PDF under Faculty_Job_Listings.
The faculty page links each opening as a PDF under Faculty_Job_Listings.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 392
SCHOOL_NAME = 'Knox College'
CAREERS_LINK = 'https://www.knox.edu/employment-at-knox/faculty'
ATS_PLATFORM = 'ADP Workforce Now'
PLATFORM = 'adp'

POSTING_RE = re.compile(r'/documents/HR/Faculty_Job_Listings/[^/]+\.pdf$')

DOC_RE = r'/documents/HR/Faculty_Job_Listings/[^/]+\.pdf$'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [link for link, _text in lib.linked_documents(CAREERS_LINK, DOC_RE)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
