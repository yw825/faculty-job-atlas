"""
Job postings scraper for school_id 1903 - EDHEC Business School (France)
ATS platform: own website
Careers link: https://www.edhec.edu/en/about-us/apply-at-edhec/professors-teachers-recruitment

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

The obvious landing page, /en/about-us/apply-at-edhec, is NOT the board: it
carries only three links, and all three are category pages
(professors-teachers-recruitment, teachers-recruitment, staff-recruitment).
The individual professor postings live one hop further in, on the
professors-teachers page used here as the careers link -- pointing this
school at the landing page would collect three category pages and zero jobs.

`professors-teachers-recruitment` and `teachers-recruitment` return
byte-identical HTML (both 284 KB), so only one is fetched; the CATEGORY
filter below drops any self-referential `*-recruitment` href so those two
plus staff-recruitment never enter the results as if they were postings.

Postings are in the static HTML, so no render is needed, and each detail
page carries schema.org JobPosting JSON-LD, which the generic detail
fetcher reads cleanly on the info side.

At the time of writing this yields 10 faculty postings (law, data science /
machine learning / econometrics, entrepreneurship, finance, retail &
quantitative marketing, two accounting, strategy x2).

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
CAREERS_LINK = BASE + '/en/about-us/apply-at-edhec/professors-teachers-recruitment'
ATS_PLATFORM = 'own website'

HREF = re.compile(r'href="(/en/about-us/apply-at-edhec/[^"#?]{6,160})"')
CATEGORY = re.compile(r'recruitment$', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=20)
    if status != 200 or not html:
        raise RuntimeError(f'edhec faculty page returned http={status}')
    links = set()
    for href in HREF.findall(html):
        href = href.rstrip('/')
        if CATEGORY.search(href):
            continue
        links.add(BASE + href)
    if not links:
        raise RuntimeError('edhec faculty page listed no postings')
    return sorted(links)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
