"""
Job postings scraper for school_id 1756 - ETH Zurich (Switzerland)
ATS platform: own website
Careers link: https://ethz.ch/en/the-eth-zurich/working-teaching-and-research/faculty/faculty-affairs/ausgeschriebene-professuren.html

CUSTOMIZED (confirmed live): postings are grouped under department/school
headings on this one page, each a real link with class "eth-link" under
the .../ausgeschriebene-professuren/... path -- titles like "Professor of
X" don't contain any word the generic default's filter looks for.
Confirmed live: 17 real postings found this way.

Writes school_job_posts/school_id_1756_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1756_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1756
SCHOOL_NAME = 'ETH Zurich'
CAREERS_LINK = 'https://ethz.ch/en/the-eth-zurich/working-teaching-and-research/faculty/faculty-affairs/ausgeschriebene-professuren.html'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

POSTING_PATH_RE = re.compile(r'/ausgeschriebene-professuren/')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for a in soup.find_all('a', class_='eth-link', href=True):
        if not POSTING_PATH_RE.search(a['href']):
            continue
        full = lib.urljoin(CAREERS_LINK, a['href'])
        if full not in seen:
            seen.add(full)
            links.append(full)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
