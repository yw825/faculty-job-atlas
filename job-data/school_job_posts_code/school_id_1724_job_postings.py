"""
Job postings scraper for school_id 1724 - University of Bergen (Norway)
ATS platform: own website
Careers link: https://www.uib.no/en/positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Bergen; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1724_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1724_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit sheet to UiB's own positions page,
which (rendered) lists every UiB vacancy as a Jobbnorge job page; only those
are kept. The old Jobbnorge employer search also returned Jobbnorge's own
home, admin and search pages.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1724
SCHOOL_NAME = 'University of Bergen'
CAREERS_LINK = 'https://www.uib.no/en/positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    links = []
    for href in re.findall(r'href="([^"]+)"', html):
        if re.search(r'jobbnorge\.no/.*/(?:job|stilling)/\d+', href) and href not in links:
            links.append(href)
    if not links:
        raise RuntimeError('no Jobbnorge postings on the positions page')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
