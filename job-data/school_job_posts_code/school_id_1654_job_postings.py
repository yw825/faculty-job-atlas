"""
Job postings scraper for school_id 1654 - Université du Québec à Trois-Rivières (Canada)
ATS platform: own website
Careers link: https://atlas.workland.com/careers/uqtr/jobs?page=1

CUSTOMIZED (confirmed live): a Workland-hosted job board (mostly French-
language postings, "[FR]: ..." titles) needing a longer render wait than
the generic default's 2s (a "Loading the list of jobs... Please wait..."
placeholder shows first) and whose "page 2" pagination link is
href="#"/JS-only, with a cookie-consent overlay that has to be dismissed
first or it intercepts the click. Confirmed live: 12 postings on page 1,
1 more on page 2 (13 total).

Writes school_job_posts/school_id_1654_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1654_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1654
SCHOOL_NAME = 'Université du Québec à Trois-Rivières'
CAREERS_LINK = 'https://atlas.workland.com/careers/uqtr/jobs?page=1'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def _work_links(html, base_url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return [lib.urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)
            if a['href'].startswith('/work/')]


def find_links():
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    page = b.new_page(user_agent=lib.UA)
    links, seen = [], set()
    try:
        page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        try:
            accept = page.get_by_text('I accept', exact=True)
            if accept.count() > 0:
                accept.first.click(timeout=3000)
                page.wait_for_timeout(1000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        for u in _work_links(page.content(), CAREERS_LINK):
            if u not in seen:
                seen.add(u)
                links.append(u)
        next_page = page.locator('a.page-link', has_text='2')
        if next_page.count() > 0:
            next_page.first.click(timeout=5000)
            page.wait_for_timeout(5000)
            for u in _work_links(page.content(), CAREERS_LINK):
                if u not in seen:
                    seen.add(u)
                    links.append(u)
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
