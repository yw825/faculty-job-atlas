"""
Job postings scraper for school_id 165 - University of Colorado Colorado Springs
ATS platform: own website
Careers link: https://jobs.colorado.edu/jobs/SearchJobs

The CU system Taleo board has no per-job URLs; Boulder's board does.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 165
SCHOOL_NAME = 'University of Colorado Colorado Springs'
CAREERS_LINK = 'https://jobs.colorado.edu/jobs/SearchJobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# cu.taleo.net keeps the requisition in session state: clicking a row lands on
# a bare jobdetail.ftl with no ?job= parameter, so there is no per-job URL to
# store. Boulder's own board does have them, and covers the CU campuses.
LISTING = 'https://jobs.colorado.edu/jobs/SearchJobs/?jobOffset={offset}'
PAGE_SIZE = 25
MAX_PAGES = 30
POSTING = re.compile(r'/jobs/JobDetail/[A-Za-z0-9][A-Za-z0-9%\-]{4,90}/\d+')


def find_links():
    seen, links = set(), []
    for page in range(MAX_PAGES):
        status, body = lib.fetch_static(LISTING.format(offset=page * PAGE_SIZE))
        if status != 200 or not body:
            break
        found = [f'https://jobs.colorado.edu{p}' for p in POSTING.findall(body)]
        fresh = [u for u in found if u not in seen]
        if not fresh:
            break
        for u in fresh:
            seen.add(u)
            links.append(u)
    if not links:
        raise RuntimeError('colorado listing returned no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
