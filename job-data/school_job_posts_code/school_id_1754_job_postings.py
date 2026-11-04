"""
Job postings scraper for school_id 1754 - University of Lausanne (Switzerland)
ATS platform: SAP SuccessFactors
Careers link: https://career5.successfactors.eu/career?company=universitdP&career_ns=job_listing_summary&navBarLevel=JOB_SEARCH&_s.crb=PsccOVQ6GYtc2oETUbXzVmM3LAk%3d

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Lausanne; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1754_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1754_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
UNIL's classic SuccessFactors list shows 10 per page; the next-page control
is clicked until a page adds nothing. A posting is stored by its
career_job_req_id without the per-session _s.crb token (the old scraper kept
tokenised links and the sign-in link, which all opened "Sign In").
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1754
SCHOOL_NAME = 'University of Lausanne'
CAREERS_LINK = 'https://career5.successfactors.eu/career?company=universitdP&career_ns=job_listing_summary&navBarLevel=JOB_SEARCH&_s.crb=PsccOVQ6GYtc2oETUbXzVmM3LAk%3d'
ATS_PLATFORM = 'SAP SuccessFactors'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    ids = []

    def walk(page):
        for _ in range(60):
            new = [x for x in re.findall(r'career_job_req_id=(\d+)', page.content()) if x not in ids]
            ids.extend(dict.fromkeys(new))
            nxt = next((el for el in page.query_selector_all('[title="Next Page"], [aria-label="Next Page"], [title="Page suivante"], [aria-label="Page suivante"]') if el.is_visible()), None)
            if not new or not nxt:
                break
            nxt.click()
            page.wait_for_timeout(4000)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000, actions=walk, timeout=90000)
    if not ids:
        raise RuntimeError(html[:200] if html else 'list did not render')
    return ['https://career5.successfactors.eu/career?career_ns=job_listing&company=universitdP'
            f'&navBarLevel=JOB_SEARCH&rcm_site_locale=en_US&career_job_req_id={i}' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
