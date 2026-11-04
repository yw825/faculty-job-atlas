"""
Job postings scraper for school_id 1856 - Macau Millennium College (Macau)
ATS platform: own website
Careers link: https://mmc.edu.mo/blog/category/notice_zh_hk/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Macau Millennium College; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1856_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1856_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Macau Millennium College posts teacher recruitment as notices
(/blog/notice_zh_hk/<n>/, e.g. "招聘教師") among general notices; the notice
category is paged (?page=N) and only notices whose title contains 招聘
("recruit") are kept. The old careers link was the contact page.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1856
SCHOOL_NAME = 'Macau Millennium College'
CAREERS_LINK = 'https://mmc.edu.mo/blog/category/notice_zh_hk/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for page in range(1, 15):
        status, html = lib.fetch_static(f'{CAREERS_LINK}?page={page}', timeout=40)
        if status != 200:
            if page == 1:
                raise RuntimeError(f'notices status={status}')
            break
        found = re.findall(r'href="(https://mmc\.edu\.mo/blog/notice_zh_hk/\d+/)"[^>]*>([^<]+)<', html)
        if not found:
            break
        for url, title in found:
            if '招聘' in title and url not in links:
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
