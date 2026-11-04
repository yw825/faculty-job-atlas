"""
Job postings scraper for school_id 1880 - Manchester Metropolitan University (United Kingdom)
ATS platform: own website
Careers link: https://manmetjobs.mmu.ac.uk/jobs/vacancy/find/results/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Manchester Metropolitan University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1880_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1880_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
eArcu board: 12 jobs per page, paged by links whose href carries
movejump_page=<n> (with a per-load pagestamp), clicked in one rendered
session. Postings are /jobs/vacancy/<slug>/<id>/description/.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1880
SCHOOL_NAME = 'Manchester Metropolitan University'
CAREERS_LINK = 'https://manmetjobs.mmu.ac.uk/jobs/vacancy/find/results/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    found = []

    def walk(page):
        for n in range(2, 60):
            for href in re.findall(r'href="([^"]*/jobs/vacancy/[^"/]+/\d+/description/?)"', page.content()):
                url = 'https://manmetjobs.mmu.ac.uk' + href if href.startswith('/') else href
                if url not in found:
                    found.append(url)
            nxt = page.query_selector(f'a[href*="movejump_page={n}&"], a[href*="movejump_page={n}"]')
            if not nxt:
                break
            nxt.click()
            page.wait_for_timeout(4000)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=6000, actions=walk, timeout=90000)
    if not found:
        raise RuntimeError(html[:200] if html else 'board did not render')
    return found


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
