"""
Job postings scraper for school_id 939 - Elmira College (US)
ATS platform: own website
Careers link: https://www.elmira.edu/welcome-to-elmira/about-ec/careers/employment-opportunities/faculty-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Elmira hosts its own openings, but splits them across THREE section pages --
faculty, staff and administrator -- so reading any single page misses most
of them. The careers link was .../careers/careers, one level above all
three, which rendered nothing job-shaped at all.

One trap here: this site emits breadcrumb links that repeat the section
prefix inside the path (.../employment-opportunities/welcome-to-elmira/
about-ec/...). Those are not postings and appear on every section, so a URL
whose path contains "welcome-to-elmira" more than once is rejected.

Writes school_job_posts/school_id_939_job_posts.csv (school_id, post_link).
Checkpointed to school_id_939_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Faculty openings are pages under /faculty-positions/.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 939
SCHOOL_NAME = 'Elmira College'
CAREERS_LINK = 'https://www.elmira.edu/welcome-to-elmira/about-ec/careers/employment-opportunities/faculty-positions'
ATS_PLATFORM = 'own website'

HOST = 'www.elmira.edu'
BASE = '/welcome-to-elmira/about-ec/careers/employment-opportunities'
SECTIONS = [f'{BASE}/faculty-positions',
            f'{BASE}/staff-positions',
            f'{BASE}/administrator-positions']

POSTING_RE = re.compile(r'^https://www\.elmira\.edu/.+/faculty-positions/[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True, wait_ms=5000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
