"""
Job postings scraper for school_id 1903 - EDHEC Business School (France)
ATS platform: own website
Careers link: https://www.edhec.edu/en/jobs

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

This school has three pages that all look like the board, and only one is:

  /en/about-us/apply-at-edhec              the landing page. NOT the board --
                                           it lists only three category pages
                                           and zero jobs.
  .../professors-teachers-recruitment      faculty only, single page, 10 posts.
                                           Used first and it under-collected.
  /en/jobs                                 the real board: same 10 posts on
                                           page 0 PLUS 9 more on page 1.

So the careers link is /en/jobs and the pages must be walked. Postings are
in the static HTML, so no render is needed, and each detail page carries
schema.org JobPosting JSON-LD, which the generic detail fetcher reads
cleanly on the info side.

Two traps in the pagination, both handled below:

  * ?page=N beyond the last page does NOT 404 and does NOT return an empty
    list -- it re-serves page 0 verbatim (page 2 came back byte-identical to
    page 0 at 288800 B). Stopping on an HTTP error or on "no links" would
    loop forever, so the loop stops when a page contributes no URL that
    earlier pages did not already have.
  * the board links its own category pages (professors-teachers-recruitment,
    staff-recruitment) alongside the real postings, so CATEGORY drops any
    self-referential *-recruitment href.

At the time of writing this yields 19 postings: 17 professorial (law, data
science, entrepreneurship, finance x2, marketing, accounting x2, strategy
x2, business ethics, geopolitics, HR, humanities, organizational behavior
x2, political sciences) and 2 non-academic.

Writes school_job_posts/school_id_1903_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1903_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1903
SCHOOL_NAME = 'EDHEC Business School'
BASE = 'https://www.edhec.edu'
CAREERS_LINK = BASE + '/en/jobs'
ATS_PLATFORM = 'own website'

HREF = re.compile(r'href="(/en/about-us/apply-at-edhec/[^"#?]{6,160})"')
CATEGORY = re.compile(r'recruitment$', re.I)
MAX_PAGES = 12  # safety net; the loop normally stops on its own

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def _postings_on(html):
    found = set()
    for href in HREF.findall(html):
        href = href.rstrip('/')
        if CATEGORY.search(href):
            continue
        found.add(BASE + href)
    return found


def find_links():
    seen = set()
    for page in range(MAX_PAGES):
        url = f'{CAREERS_LINK}?page={page}'
        status, html = lib.fetch_static(url, timeout=20)
        if status != 200 or not html:
            if page == 0:
                raise RuntimeError(f'edhec board page 0 returned http={status}')
            break
        new = _postings_on(html) - seen
        # a page past the end re-serves page 0, so "nothing new" is the end
        if page and not new:
            break
        seen |= new
    if not seen:
        raise RuntimeError('edhec board listed no postings')
    return sorted(seen)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
