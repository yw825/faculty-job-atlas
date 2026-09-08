"""
Job postings scraper for school_id 204 - George Washington University (US)
ATS platform: own website
Careers link: https://careers.gwu.edu/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for George Washington University; nothing here affects any
other school's script.

Link check (ok): 5 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_204_job_posts.csv (school_id, post_link).
Checkpointed to school_id_204_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 204
SCHOOL_NAME = 'George Washington University'
CAREERS_LINK = 'https://careers.gwu.edu/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_PATTERN = 'careers.gwu.edu/<*>'


def find_links():
    """CUSTOMIZED: postings on this site are the links matching one repeated
    URL shape, found structurally rather than by keyword and then confirmed
    by opening two of them and checking they read like job postings
    (title_role=0 degree=0 furniture=0 len=4157; title_role=0 degree=0 furniture=2 len=8828).

        careers.gwu.edu/<*>

    The generic job-word filter returned 1 link(s) here against 2
    actually on the page -- this site's posting URLs carry no job word at
    all, which is why matching on words missed them."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import deep_probe

    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        if deep_probe.templatize(href, CAREERS_LINK) == POSTING_PATTERN:
            full = urljoin(CAREERS_LINK, href)
            if full not in out:
                out.append(full)
    return out


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
