"""
Job postings scraper for school_id 1881 - Leeds Beckett University (United Kingdom)
ATS platform: own website
Careers link: https://vacancies.leedsbeckett.ac.uk/ce0984li_webrecruitment/wrd/run/ETREC105GF.open?WVID=7412577lKO&LANG=USA

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Leeds Beckett University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1881_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1881_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Unit4 web recruitment: the search form's button is submitted, results show
10 per page with a "Next" button (BU_NEXT), and vacancy links carry a
per-visit USESSION. Postings are stored session-free as
ETREC107GF.open?VACANCY_ID=<id>&WVID=..&LANG=USA, which opens the job.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1881
SCHOOL_NAME = 'Leeds Beckett University'
CAREERS_LINK = 'https://vacancies.leedsbeckett.ac.uk/ce0984li_webrecruitment/wrd/run/ETREC105GF.open?WVID=7412577lKO&LANG=USA'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    ids = []
    base = 'https://vacancies.leedsbeckett.ac.uk/ce0984li_webrecruitment/wrd/run/'

    def walk(page):
        try:
            with page.expect_navigation(timeout=30000, wait_until='networkidle'):
                page.click('[id="BU_SEARCH.FRM_BUTTON.ET_BASE.1-1"]')
        except Exception:
            pass
        for _ in range(40):
            page.wait_for_timeout(4000)
            new = [i for i in re.findall(r'VACANCY_ID(?:%3d|%3D|=)(\w+)', page.content()) if i not in ids]
            ids.extend(dict.fromkeys(new))
            nxt = page.query_selector('[id="BU_NEXT.FRM_BUTTON.ET_BASE.1-1-1_link"]')
            if not new or not nxt or not nxt.is_visible():
                break
            try:  # the visible "Next" is a link beside a hidden submit input
                with page.expect_navigation(timeout=20000, wait_until='networkidle'):
                    nxt.evaluate('e => e.click()')
            except Exception:
                pass
    lib.fetch_rendered(base + 'ETREC105GF.open?WVID=7412577lKO&LANG=USA', wait_ms=4000, actions=walk, timeout=90000)
    if not ids:
        raise RuntimeError('no vacancies found (search did not run)')
    return [f'{base}ETREC107GF.open?VACANCY_ID={i}&WVID=7412577lKO&LANG=USA' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
