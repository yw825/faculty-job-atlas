"""
Job postings scraper for school_id 1674 - ESSEC Business School (France)
ATS platform: own website
Careers link: https://job.essec.edu/en/jobs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for ESSEC Business School; nothing here affects any
other school's script.

TUNED FIND_LINKS
The audit marked this school "0 post": nothing was listed, so no posting
URL shape could be pinned. Until one appears, only main-content links whose
TEXT names an academic role are kept, which stops the generic scraper's
navigation links (careers hub, repository, alumni pages) being stored.

Writes school_job_posts/school_id_1674_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1674_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1674
SCHOOL_NAME = 'ESSEC Business School'
CAREERS_LINK = 'https://job.essec.edu/en/jobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


ROLE_RE = re.compile(r'professor|professeur|lecturer|chargé|charge de cours|postdoc|post-doc|'
                     r'postdoctoral|chercheur|researcher|faculty|enseignant|chair|chaire', re.I)


def find_links():
    """No opening was listed when this was written ("0 post" in the audit),
    so there is no posting URL shape to match yet: keep only links inside
    the page's main content whose own text names an academic role."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['nav', 'header', 'footer', 'script', 'style']):
        tag.decompose()
    main = soup.select_one('main') or soup
    links = []
    for a in main.find_all('a', href=True):
        url = urljoin(CAREERS_LINK, a['href'].strip())
        text = a.get_text(' ', strip=True)
        if (url.startswith('http') and ROLE_RE.search(text) and url.split('#')[0] != CAREERS_LINK.split('#')[0]
                and not re.search(r'/(?:opportunities|offres)/[^/]+/?$', url) and url not in links):
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
