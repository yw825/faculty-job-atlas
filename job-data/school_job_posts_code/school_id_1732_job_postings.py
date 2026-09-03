"""
Job postings scraper for school_id 1732 - Nova School of Business and Economics (Portugal)
ATS platform: own website
Careers link: https://www.novasbe.unl.pt/en/about-us/join-our-school/faculty-and-researchers?_gl=1*1dkl70r*_up*MQ..*_ga*MTQ3NjQyMTUwOC4xNzg4Mjg5Nzc1*_ga_NRJH2682FN*czE3ODgyODk3NzMkbzEkZzAkdDE3ODgyODk3NzMkajYwJGwwJGg3NTg5MTkxNDk.

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Nova School of Business and Economics; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1732_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1732_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1732
SCHOOL_NAME = 'Nova School of Business and Economics'
CAREERS_LINK = 'https://www.novasbe.unl.pt/en/about-us/join-our-school/faculty-and-researchers?_gl=1*1dkl70r*_up*MQ..*_ga*MTQ3NjQyMTUwOC4xNzg4Mjg5Nzc1*_ga_NRJH2682FN*czE3ODgyODk3NzMkbzEkZzAkdDE3ODgyODk3NzMkajYwJGwwJGg3NTg5MTkxNDk.'
ATS_PLATFORM = 'own website'

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
