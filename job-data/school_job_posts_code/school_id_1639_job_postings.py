"""
Job postings scraper for school_id 1639 - Université du Québec en Outaouais (Canada)
ATS platform: own website
Careers link: https://uqo.ca/direction-services/decanat-gestion-academique/postes-professeurs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Université du Québec en Outaouais; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is a document, uqo.ca/docs/<id>, linked by its discipline
("Kinésiologie"). The page links other documents the same way -- the
candidate guide, the employment-equity programme -- so links whose text
names a guide or policy are skipped.

Writes school_job_posts/school_id_1639_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1639_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1639
SCHOOL_NAME = 'Université du Québec en Outaouais'
CAREERS_LINK = 'https://uqo.ca/direction-services/decanat-gestion-academique/postes-professeurs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://uqo\.ca/docs/\d+$', re.I)


DOC_RE = re.compile(r'^https://uqo\.ca/docs/\d+$', re.I)
NOT_A_POSTING_RE = re.compile(r'guide|égalité|egalite|équité|equite|politique|règlement|reglement|convention', re.I)


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    links = []
    for a in BeautifulSoup(html, 'html.parser').find_all('a', href=True):
        url = urljoin(CAREERS_LINK, a['href'])
        if DOC_RE.search(url) and not NOT_A_POSTING_RE.search(a.get_text(' ', strip=True)) and url not in links:
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
