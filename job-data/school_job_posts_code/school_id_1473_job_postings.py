"""
Job postings scraper for school_id 1473 - James Madison University (US)
ATS platform: own website (PageUp career site)
Careers link: https://jobs.jmu.edu/jobs/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Two things defeated the generic scrape. The board's home page renders no
postings at all -- they appear only under /jobs/search, and only after the
page's own JS has run behind an AWS WAF challenge, which takes some seconds.
And a posting's URL is a pure SLUG with no numeric id
(/jobs/assistant-professor-of-english-linguistics-tenure-track-harrisonburg-
virginia-united-states), so every id-shaped pattern missed them; the school
recorded one link.

Matching the slug path directly finds the real openings, faculty among them
("Tenure-Track Assistant/Associate Professor, Social Work", "Nursing
Faculty, Women's Health - Lecturer").

Writes school_job_posts/school_id_1473_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1473_job_postings.checkpoint next to this script.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1473
SCHOOL_NAME = 'James Madison University'
CAREERS_LINK = 'https://jobs.jmu.edu/jobs/search'
ATS_PLATFORM = 'own website'

HOST = 'jobs.jmu.edu'
# /jobs/<slug>, but not the search page itself and not the candidate account.
POSTING_PATH = re.compile(r'^/jobs/(?!search\b)[a-z0-9][a-z0-9\-]{8,200}$', re.I)
RENDER_WAIT_MS = 16000

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=RENDER_WAIT_MS)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for a in soup.find_all('a', href=True):
        full = urljoin(CAREERS_LINK, a['href'].strip())
        parsed = urlparse(full)
        if parsed.netloc != HOST or not POSTING_PATH.match(parsed.path):
            continue
        clean = f'https://{HOST}{parsed.path}'
        if clean not in seen:
            seen.add(clean)
            links.append(clean)
    if not links:
        raise RuntimeError('jmu job search rendered no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
