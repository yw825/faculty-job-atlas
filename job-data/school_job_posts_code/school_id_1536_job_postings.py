"""
Job postings scraper for school_id 1536 - Marian University (US)
ATS platform: own website
Careers link: https://www.marianuniversity.edu/about-marian/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Marian publishes each opening as an ordinary page at the top level of its
own site -- /adjunct-accounting/, /assistant-mens-bowling-coach/ -- with the
job title as the link text. Neither the href nor the title contains a
"job"/"career"/"posting" word, so the generic href filter found nothing
while a loose slug pattern swept up /academics/ and /about-marian/ alongside
the real ones.

What separates a posting from navigation here is the LINK TEXT naming a role
("Adjunct, Accounting", "Assistant Coach, Men's Bowling"), so that is what
this matches, restricted to single-segment paths on Marian's own host.

Writes school_job_posts/school_id_1536_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1536_job_postings.checkpoint next to this script.
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1536
SCHOOL_NAME = 'Marian University'
CAREERS_LINK = 'https://www.marianuniversity.edu/about-marian/employment/'
ATS_PLATFORM = 'own website'

# The link text of a posting names a role. Deliberately does NOT include bare
# "faculty"/"staff", which are navigation labels on this site.
ROLE = re.compile(r'\b(adjunct|professor|instructor|lecturer|dean|chair|'
                  r'coach|director|coordinator|manager|specialist|analyst|'
                  r'officer|nurse|counselor|librarian|technician|advisor|'
                  r'assistant|associate)\b', re.I)
# A posting's slug always names a role in several words -- adjunct-accounting,
# director-of-hospitality. A single bare word is an office: /registrar/ was
# collected by the first version of this filter because the site's nav links
# it as "Registrar", which the role pattern matches.
SINGLE_SEGMENT = re.compile(r'^/[a-z0-9]+(?:-[a-z0-9]+)+/?$', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=8000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for a in soup.find_all('a', href=True):
        text = a.get_text(' ', strip=True)
        if not ROLE.search(text):
            continue
        full = urljoin(CAREERS_LINK, a['href'].strip())
        parsed = urlparse(full)
        if parsed.netloc != 'www.marianuniversity.edu':
            continue
        if not SINGLE_SEGMENT.match(parsed.path):
            continue
        clean = f'https://{parsed.netloc}{parsed.path}'
        if clean not in seen:
            seen.add(clean)
            links.append(clean)
    if not links:
        raise RuntimeError('marian employment page listed no role-titled links')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
