"""
Job postings scraper for school_id 939 - Elmira College (US)
ATS platform: own website
Careers link: https://www.elmira.edu/welcome-to-elmira/about-ec/careers/employment-opportunities/overview

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
"""
import os
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 939
SCHOOL_NAME = 'Elmira College'
CAREERS_LINK = ('https://www.elmira.edu/welcome-to-elmira/about-ec/careers/'
                'employment-opportunities/overview')
ATS_PLATFORM = 'own website'

HOST = 'www.elmira.edu'
BASE = '/welcome-to-elmira/about-ec/careers/employment-opportunities'
SECTIONS = [f'{BASE}/faculty-positions',
            f'{BASE}/staff-positions',
            f'{BASE}/administrator-positions']

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    links, seen, failures = [], set(), []
    for section in SECTIONS:
        url = f'https://{HOST}{section}'
        html = lib.fetch_rendered(url, wait_ms=8000)
        if lib.is_fetch_failure(html):
            failures.append(f'{section}: {html[:50]}')
            continue
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            full = urljoin(url, a['href'].strip())
            parsed = urlparse(full)
            if parsed.netloc != HOST:
                continue
            path = parsed.path.rstrip('/')
            # must sit UNDER this section, and not be the section itself
            if not path.startswith(section) or path == section:
                continue
            # breadcrumb links repeat the site prefix inside the path
            if path.count('welcome-to-elmira') > 1:
                continue
            clean = f'https://{HOST}{path}'
            if clean not in seen:
                seen.add(clean)
                links.append(clean)
    if not links:
        raise RuntimeError('no postings in any elmira section; '
                           + ' | '.join(failures))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
