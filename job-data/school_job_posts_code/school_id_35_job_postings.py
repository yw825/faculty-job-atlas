"""
Job postings scraper for school_id 35 - University of the Ozarks (US)
ATS platform: own website
Careers link: https://ozarks.edu/about/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of the Ozarks; nothing here affects any
other school's script.

Link check (ok): 3 posting-shaped links found.

TUNED FIND_LINKS
Each opening is a PDF ad (/wp-content/uploads/<ad>.pdf) linked from a
paragraph of the employment article. Other PDFs on the page -- the Clery
report -- are buttons, not paragraph links, so the selector skips them.

Writes school_job_posts/school_id_35_job_posts.csv (school_id, post_link).
Checkpointed to school_id_35_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 35
SCHOOL_NAME = 'University of the Ozarks'
CAREERS_LINK = 'https://ozarks.edu/about/employment/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_PATTERN = 'ozarks.edu/news/<*>'


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.select('article p a[href$=".pdf"]'):
        url = urljoin(CAREERS_LINK, a['href'])
        if '/wp-content/uploads/' in url and url not in links:
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
