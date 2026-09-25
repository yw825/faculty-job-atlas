"""
Job postings scraper for school_id 1543 - Edgewood College (US)
ATS platform: own website
Careers link: https://www.edgewood.edu/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

The careers link was https://www.edgewood.edu/employment/human-resources-
generalist/ -- ONE job, not the board. So the school could only ever record
that single posting, and would have recorded nothing once it was filled.

Edgewood hosts its own openings as pages under /employment/, titled by role
("Adjunct Instructor - Biology (General Call)", "Adjunct Clinical Instructor
- Online Accelerated Nursing Program"). Twenty are listed.

Postings are distinguished from section pages by their multi-word slug:
/employment/adjunct-instructor-biology/ is a posting, /employment/benefits/
would not be. The index itself is excluded.

Writes school_job_posts/school_id_1543_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1543_job_postings.checkpoint next to this script.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1543
SCHOOL_NAME = 'Edgewood College'
CAREERS_LINK = 'https://www.edgewood.edu/employment/'
ATS_PLATFORM = 'own website'

HOST = 'www.edgewood.edu'
# /employment/<multi-word-slug>/ -- a hyphen usually means a role title
# rather than a section page.
POSTING_PATH = re.compile(r'^/employment/[a-z0-9]+(?:-[a-z0-9]+)+/?$', re.I)
# ...but not always: /employment/new-hire/ is onboarding paperwork and is
# hyphenated exactly like /employment/custodial-manager/. Shape cannot
# separate these, so the few non-postings under /employment/ are named.
NOT_A_POSTING = {'new-hire', 'new-hires', 'how-to-apply', 'employee-benefits',
                 'equal-opportunity', 'why-edgewood'}

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=8000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for a in soup.find_all('a', href=True):
        full = urljoin(CAREERS_LINK, a['href'].strip())
        parsed = urlparse(full)
        if parsed.netloc != HOST or not POSTING_PATH.match(parsed.path):
            continue
        if parsed.path.strip('/').split('/')[-1].lower() in NOT_A_POSTING:
            continue
        clean = f'https://{HOST}{parsed.path}'
        if clean not in seen:
            seen.add(clean)
            links.append(clean)
    if not links:
        raise RuntimeError('edgewood employment index listed no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
