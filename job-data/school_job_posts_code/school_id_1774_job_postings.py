"""
Job postings scraper for school_id 1774 - University College London (United Kingdom)
ATS platform: own website (TalentLink widget embedded directly in the page)

CUSTOMIZED (confirmed live): this page is NOT actually blocked by anything --
it just needs its cookie-consent banner ("Accept all cookies") clicked before
the embedded TalentLink vacancy widget renders. There is no iframe involved
(unlike icims/IE University) -- the widget renders inline in the top document
once the banner is dismissed. After accepting cookies, the results list is
already populated (no need to click "Search" separately, but doing so is
harmless and used here for robustness). "Show more results" is a
load-more button; clicked repeatedly until it disappears or stops adding
new jobIds. Confirmed live: 12 unique jobId postings on one run.

Posting URLs are of the form:
  https://www.ucl.ac.uk/work-at-ucl/search-ucl-jobs/details?jobId=<id>&jobTitle=<title>

Writes school_job_posts/school_id_1774_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1774_job_postings.checkpoint next to this script.
"""
import os
import re
import sys
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1774
SCHOOL_NAME = 'University College London'
CAREERS_LINK = 'https://www.ucl.ac.uk/work-at-ucl/search-ucl-jobs'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

JOB_ID_RE = re.compile(r'href="([^"]*details\?jobId=\d+[^"]*)"')


def find_links():
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')

    page = b.new_page(user_agent=lib.UA)
    try:
        page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        try:
            page.get_by_text('Accept all cookies', exact=False).first.click(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        try:
            page.get_by_text('Search', exact=True).first.click(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(3000)

        for _ in range(30):
            try:
                btn = page.get_by_text('Show more results', exact=False)
                if btn.count() == 0:
                    break
                btn.first.click(timeout=3000)
                page.wait_for_timeout(1500)
            except Exception:
                break

        html = page.content()
    finally:
        page.close()

    if lib.is_fetch_failure(html):
        raise RuntimeError(html)

    links = []
    seen = set()
    for href in JOB_ID_RE.findall(html):
        href = unescape(href)
        if not href.startswith('http'):
            href = 'https://www.ucl.ac.uk' + href
        m = re.search(r'jobId=(\d+)', href)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            links.append(href)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
