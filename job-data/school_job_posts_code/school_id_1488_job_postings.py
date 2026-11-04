"""
Job postings scraper for school_id 1488 - Roanoke College (US)
ATS platform: JobScore
Careers link: https://careers.jobscore.com/careers/roanokecollege

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Roanoke does not host its openings. Its careers link was
roanoke.edu/inside/human_resources/jobs_roanoke, from which the generic
filter collected eleven navigation links (academic program pages, alumni
content) and no postings.

The college's board is JobScore. Note roanoke.edu/jobs is not usable as a
substitute: it returns a megabyte of HTML containing zero job links, because
the listing is injected by script -- the vendor board is the only route.

Postings are linked relatively (/careers/roanokecollege/jobs/<slug>-<id>),
so they are resolved against the JobScore host here.

Writes school_job_posts/school_id_1488_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1488_job_postings.checkpoint next to this script.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1488
SCHOOL_NAME = 'Roanoke College'
CAREERS_LINK = 'https://careers.jobscore.com/careers/roanokecollege'
ATS_PLATFORM = 'JobScore'

HOST = 'careers.jobscore.com'
POSTING_PATH = re.compile(r'^/careers/roanokecollege/jobs/[A-Za-z0-9][\w\-]{6,160}$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=9000)
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
        raise RuntimeError('roanoke jobscore board listed no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
