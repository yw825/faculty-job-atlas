"""
Job postings scraper for school_id 1889 - Eindhoven University of Technology (Netherlands)
ATS platform: own website
Careers link: https://www.tue.nl/en/working-at-tue/vacancy-overview

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Eindhoven University of Technology; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1889_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1889_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
TU/e's overview shows 12 vacancies and a "more" button that adds 12 per
click (43 in all); it is clicked until it disappears. Postings are
/vacancy-overview/<slug> (not the filter links the old scraper kept).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1889
SCHOOL_NAME = 'Eindhoven University of Technology'
CAREERS_LINK = 'https://www.tue.nl/en/working-at-tue/vacancy-overview'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    def load_all(page):
        # A cookie banner covers the page in a fresh browser; the "Load
        # more" link is only clickable once it is dismissed.
        deny = page.query_selector('button:has-text("Deny")')
        if deny and deny.is_visible():
            deny.click()
            page.wait_for_timeout(2000)
        for _ in range(20):
            more = page.query_selector('button:has-text("more"), a:has-text("Load more"), '
                                       'button:has-text("Show more"), a:has-text("Show more")')
            if not more or not more.is_visible():
                break
            more.click()
            page.wait_for_timeout(2500)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000, actions=load_all, timeout=90000)
    if not html or lib.is_fetch_failure(html):
        raise RuntimeError(html or 'overview did not render')
    links = []
    for slug in re.findall(r'/en/working-at-tue/vacancy-overview/([a-z0-9-]+)"', html):
        url = f'https://www.tue.nl/en/working-at-tue/vacancy-overview/{slug}'
        if url not in links:
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
