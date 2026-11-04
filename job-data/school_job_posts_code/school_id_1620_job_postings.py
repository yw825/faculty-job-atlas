"""
Job postings scraper for school_id 1620 - Queen's University (Canada)
ATS platform: own website
Careers link: https://www.queensu.ca/faculty-positions/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Queen's University; nothing here affects any
other school's script.

TUNED FIND_LINKS
The page is grouped by faculty; each faculty has a collapsible
"Tenure-track positions" button whose panel (aria-controls ->
card-body-<id>) links that faculty's postings -- department pages, PDF ads,
the occasional SharePoint file. Every link in those panels is a posting;
the sibling "Links to other academic positions" panels are not read.

Writes school_job_posts/school_id_1620_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1620_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1620
SCHOOL_NAME = "Queen's University"
CAREERS_LINK = 'https://www.queensu.ca/faculty-positions/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for button in soup.select('button[aria-controls]'):
        if 'tenure-track positions' not in button.get_text(' ', strip=True).lower():
            continue
        panel = soup.find(id=button['aria-controls'])
        for a in (panel.find_all('a', href=True) if panel else []):
            url = urljoin(CAREERS_LINK, a['href'].strip())
            if url.startswith('http') and url not in links:
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
