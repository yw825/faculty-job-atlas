"""
Job postings scraper for school_id 82 - Pomona College (US)
ATS platform: own website
Careers link: https://www.pomona.edu/administration/academic-dean/faculty-jobs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Pomona College; nothing here affects any
other school's script.

Link check (ok): 8 posting-shaped links found.

TUNED FIND_LINKS
Openings are accordion tabs on this page, grouped under "Tenure Track
Positions" and "Temporary Faculty Positions"; clicking a tab opens the full
ad. Each tab has a stable data-accordion-id, so each opening is stored as
this page plus #<that id> (e.g. #assistant-professor-of-biology). The apply
links inside the tabs (AcademicJobsOnline, Workday) are not stored
separately. tabs() and page_html() are reused by this school's info script.

Writes school_job_posts/school_id_82_job_posts.csv (school_id, post_link).
Checkpointed to school_id_82_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 82
SCHOOL_NAME = 'Pomona College'
CAREERS_LINK = 'https://www.pomona.edu/administration/academic-dean/faculty-jobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def tabs(html, base_url=CAREERS_LINK):
    """[(url#accordion-id, title, body)] -- one per accordion tab."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for header in soup.select('.js-accordion__header[data-accordion-id]'):
        content = header.find_next_sibling('div')
        body = content.get_text(' ', strip=True) if content else ''
        out.append((f"{base_url}#{header['data-accordion-id']}",
                    header.get_text(' ', strip=True), body[:20000]))
    return out


def page_html():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    return html


def find_links():
    return [u for u, _t, _b in tabs(page_html())]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
