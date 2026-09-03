"""
Job postings scraper for school_id 1783 - Southern Cross University (Australia)
ATS platform: PageUp/NGA
Careers link: https://scu.nga.net.au/cp/index.cfm?event=jobs.home&CurATC=SCUV&CurBID=51DD8D38%2D4B88%2D7392%2DACDD%2DED0640CCE5F0&persistVariables=CurATC,CurBID&rmuh=15EDB634969DDC3C00315ACF8D676E85FD9E305F

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Southern Cross University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1783_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1783_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1783
SCHOOL_NAME = 'Southern Cross University'
CAREERS_LINK = 'https://scu.nga.net.au/cp/index.cfm?event=jobs.home&CurATC=SCUV&CurBID=51DD8D38%2D4B88%2D7392%2DACDD%2DED0640CCE5F0&persistVariables=CurATC,CurBID&rmuh=15EDB634969DDC3C00315ACF8D676E85FD9E305F'
ATS_PLATFORM = 'PageUp/NGA'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK,
                              href_pattern=lib.COMMON_JOB_URL_HINTS,
                              text_pattern=lib.COMMON_JOB_URL_HINTS)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
