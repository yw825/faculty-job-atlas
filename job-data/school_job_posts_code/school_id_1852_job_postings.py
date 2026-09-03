"""
Job postings scraper for school_id 1852 - Macao University of Science and Technology (Macau)
ATS platform: own website
Careers link: https://careers.must.edu.mo/recruitment-latest?locale=en_US

CUSTOMIZED (confirmed live): a Vue.js app that shows "No data available"
until the "Academic and Research Positions" type filter is clicked (a plain
JS click handler, no query param equivalent found). Each result's "Details"
button is also JS-only (no href, no id anywhere in the DOM) but clicking it
navigates to a real, stable URL
("recruitment-latest-details?0=<id>&from=RecruitmentLatest") -- so each one
has to be clicked individually to learn its URL, same approach as
job_postings_lib.scrape_icims used to before this file's own investigation
found icims' pagination links were plain hrefs (this site has no such
shortcut). Confirmed live: 15 postings on the one visible page.

Writes school_job_posts/school_id_1852_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1852_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1852
SCHOOL_NAME = 'Macao University of Science and Technology'
CAREERS_LINK = 'https://careers.must.edu.mo/recruitment-latest?locale=en_US'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def _open_filtered_list(page):
    page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
    page.wait_for_timeout(3000)
    page.get_by_text('Academic and Research Positions', exact=True).first.click(timeout=5000)
    page.wait_for_timeout(3000)


def find_links():
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')

    page = b.new_page(user_agent=lib.UA)
    try:
        _open_filtered_list(page)
        count = page.get_by_text('Details', exact=True).count()
    finally:
        page.close()
    if count == 0:
        raise RuntimeError('no "Details" buttons found -- page structure may have changed')

    links = []
    for idx in range(count):
        for attempt in range(2):
            page = b.new_page(user_agent=lib.UA)
            try:
                _open_filtered_list(page)
                loc = page.get_by_text('Details', exact=True)
                if idx >= loc.count():
                    break
                loc.nth(idx).click(timeout=5000)
                page.wait_for_timeout(2000)
                if 'recruitment-latest-details' in page.url:
                    links.append(page.url)
                break
            except Exception:
                pass  # one posting failing to load isn't worth losing the rest of the school over
            finally:
                page.close()
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
