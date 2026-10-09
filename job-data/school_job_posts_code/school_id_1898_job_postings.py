"""
Job postings scraper for school_id 1898 - CATÓLICA-LISBON School of Business & Economics (Portugal)
Careers link: https://clsbe.lisboa.ucp.pt/research/research-positions

TUNED FIND_LINKS
The research-positions page has tables per section -- "Faculty Positions",
"PhD researchers" and "Research fellowships" -- with POSITION / ADMISSION
REQUIREMENTS / DEADLINE / STATUS columns. Rows of the first two sections
whose STATUS is "Open" are collected (their PDF); research fellowships
(student grants) and closed calls with published results are not. The old
scraper took every PDF on the page, the faculty directory included.

Writes school_job_posts/school_id_1898_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1898_job_postings.checkpoint next to this script.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1898
SCHOOL_NAME = 'CATÓLICA-LISBON School of Business & Economics'
CAREERS_LINK = 'https://clsbe.lisboa.ucp.pt/research/research-positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=40)
    if status != 200:
        raise RuntimeError(f'research positions status={status}')
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for h2 in soup.find_all('h2'):
        if h2.get_text(strip=True) not in ('Faculty Positions', 'PhD researchers'):
            continue
        section = h2.find_parent(['details', 'section']) or h2.parent
        for _ in range(3):
            if section.find('tr') or section.find('a', href=re.compile(r'\.pdf')):
                break
            section = section.parent
        for row in section.find_all('tr'):
            cells = [c.get_text(' ', strip=True) for c in row.find_all(['td', 'th'])]
            if not cells or not re.search(r'(?i)^open$', cells[-1]):
                continue
            a = row.find('a', href=re.compile(r'\.pdf'))
            if a and urljoin(CAREERS_LINK, a['href']) not in links:
                links.append(urljoin(CAREERS_LINK, a['href']))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
