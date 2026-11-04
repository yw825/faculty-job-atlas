"""
Job postings scraper for school_id 1715 - University of Luxembourg (Luxembourg)
ATS platform: own website
Careers link: https://www.uni.lu/en/about/work/explore-our-jobs/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Luxembourg; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1715_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1715_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
uni.lu's job list sits behind a CloudFront firewall that blocks the bundled
headless browser; installed Chrome (lib.get_real_chrome) passes. The list
shows 9 jobs and a "Load more" button, clicked until it disappears.
Postings are /en/jobs/<slug>/.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1715
SCHOOL_NAME = 'University of Luxembourg'
CAREERS_LINK = 'https://www.uni.lu/en/about/work/explore-our-jobs/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    page = lib.get_real_chrome().new_page()
    try:
        page.goto(CAREERS_LINK, timeout=90000)
        page.wait_for_timeout(6000)
        for _ in range(30):
            more = page.query_selector('button:has-text("Load more"), a:has-text("Load more")')
            if not more or not more.is_visible():
                break
            more.click()
            page.wait_for_timeout(2500)
        html = page.content()
    finally:
        page.close()
    links = []
    for href in re.findall(r'href="((?:https://www\.uni\.lu)?/en/jobs/[a-z0-9-]+/?)"', html):
        url = href if href.startswith('http') else 'https://www.uni.lu' + href
        if url not in links:
            links.append(url)
    if not links:
        raise RuntimeError('no jobs on the page (blocked?)')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
