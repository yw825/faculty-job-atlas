"""
Job postings scraper for school_id 1891 - Aalborg University (Denmark)
ATS platform: own website
Careers link: https://www.vacancies.aau.dk/scientific-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Aalborg University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1891_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1891_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit sheet to the scientific-positions list,
which renders its vacancies as show-vacancy/vacancyId/<n> links.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1891
SCHOOL_NAME = 'Aalborg University'
CAREERS_LINK = 'https://www.vacancies.aau.dk/scientific-positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    links = []
    for href in re.findall(r'href="([^"]*show-vacancy/vacancyId/\d+)[^"]*"', html):
        url = href if href.startswith('http') else 'https://www.vacancies.aau.dk' + href
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
