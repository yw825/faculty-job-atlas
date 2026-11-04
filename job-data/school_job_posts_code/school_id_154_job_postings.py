"""
Job postings scraper for school_id 154 - Humphreys University-Stockton and Modesto Campuses (US)
ATS platform: own website
Careers link: https://www.humphreys.edu/career-opportunities/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Humphreys University-Stockton and Modesto Campuses; nothing here affects any
other school's script.

Link check (review): 2 posting-shaped links found -- rendered few job-shaped links.

TUNED FIND_LINKS
Openings are listed inside the page's <article> under "Current Openings";
everything outside it is site navigation, which is what the generic filter
used to store. On 2026-10-07 the article read "No openings available.", so
no posting has been seen yet to pin a URL shape -- any link the article
gains is taken as an opening.

Writes school_job_posts/school_id_154_job_posts.csv (school_id, post_link).
Checkpointed to school_id_154_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 154
SCHOOL_NAME = 'Humphreys University-Stockton and Modesto Campuses'
CAREERS_LINK = 'https://www.humphreys.edu/career-opportunities/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    article = BeautifulSoup(html, 'html.parser').select_one('article')
    if article is None:
        raise RuntimeError('humphreys: no article on the careers page')
    if re.search(r'No openings available', article.get_text(' ', strip=True), re.I):
        return []
    page = CAREERS_LINK.rstrip('/')
    return [u for u in lib.extract_links(str(article), CAREERS_LINK)
            if u.split('#')[0].rstrip('/') != page]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
