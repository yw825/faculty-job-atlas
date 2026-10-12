"""
Job postings scraper for school_id 1845 - The Hong Kong University of Science and Technology (Hong Kong)
ATS platform: own website
Careers link: https://hkustcareers.hkust.edu.hk/join-us/current-opening/academic-careers

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for The Hong Kong University of Science and Technology; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1845_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1845_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
HKUST's academic-careers page links two systems: PeopleSoft postings
(HRS_CE ... JobOpeningId=<n>) and Interfolio (apply.interfolio.com/<n>, the
audit's example). The page shows only part of the Interfolio jobs, so the
whole Interfolio board (21935) is read as well; menu links are dropped.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1845
SCHOOL_NAME = 'The Hong Kong University of Science and Technology'
CAREERS_LINK = 'https://hkustcareers.hkust.edu.hk/join-us/current-opening/academic-careers'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    links = []
    for href in re.findall(r'href="([^"]+)"', html):
        href = href.replace('&amp;', '&')
        if re.search(r'JobOpeningId=\d+|apply\.interfolio\.com/\d+$', href) and href not in links:
            links.append(href)
    for url in lib.scrape_interfolio('https://apply.interfolio.com/21935/positions'):
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
