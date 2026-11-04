"""
Job postings scraper for school_id 1867 - Temasek Polytechnic (Singapore)
ATS platform: own website
Careers link: https://www.careers.hrp.gov.sg/sap/bc/ui5_ui5/sap/ZGERCFA004/index.html?search-keyword=temasek

CUSTOMIZED (confirmed live): this is a SAP UI5 single-page app (Singapore
government careers portal), same platform as school_id 1864 (Ngee Ann
Polytechnic) -- see that script's docstring for the full investigation.
Every job title link has href="#" with pure JS click handling, no static
per-posting URL to extract -- BUT clicking a title updates the page to a
real, stable, bookmarkable hash route (".../index.html?search-keyword=...
#/JobDescription/<id>/<guid>"). Each posting has to be clicked individually
to learn its real URL; this reloads the search page fresh before each click
(simplest way to avoid the SPA's list re-render state going stale between
clicks).

Also confirmed live: `wait_until='networkidle'` (fetch_rendered's usual
escalation path) times out here -- this page has a recurring background
analytics beacon that never lets the network go fully idle. Waiting for
the job-title link selector directly is reliable where networkidle isn't.

Writes school_job_posts/school_id_1867_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1867_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1867
SCHOOL_NAME = 'Temasek Polytechnic'
CAREERS_LINK = 'https://www.careers.hrp.gov.sg/sap/bc/ui5_ui5/sap/ZGERCFA004/index.html?search-keyword=temasek'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

TITLE_LINK_SELECTOR = 'a.customJobSearchTitle'


def find_links():
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')

    def load_titles():
        last_err = None
        for _ in range(3):
            page = b.new_page(user_agent=lib.UA)
            try:
                page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
                page.wait_for_selector(TITLE_LINK_SELECTOR, timeout=20000)
                return [t.strip() for t in page.locator(TITLE_LINK_SELECTOR).all_inner_texts()]
            except Exception as e:
                last_err = e
            finally:
                page.close()
        raise RuntimeError(f'could not load job list after 3 attempts: {last_err}')

    titles = load_titles()
    if not titles:
        raise RuntimeError('no job title links found -- page structure may have changed')

    links = []
    for idx in range(len(titles)):
        for attempt in range(2):
            page = b.new_page(user_agent=lib.UA)
            try:
                page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
                page.wait_for_selector(TITLE_LINK_SELECTOR, timeout=20000)
                loc = page.locator(TITLE_LINK_SELECTOR)
                if idx >= loc.count():
                    break
                loc.nth(idx).click(timeout=5000)
                page.wait_for_timeout(1500)
                if '#/JobDescription/' in page.url:
                    links.append(page.url)
                break
            except Exception:
                pass  # one posting failing to load isn't worth losing the rest of the school over
            finally:
                page.close()
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
