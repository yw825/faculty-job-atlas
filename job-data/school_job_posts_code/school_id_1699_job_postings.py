"""
Job postings scraper for school_id 1699 - Eötvös Loránd University (Hungary)
ATS platform: own website
Careers link: https://www.elte.hu/en/work-opportunities

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Eötvös Loránd University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is a PDF in ELTE's document store,
elte.hu/(en/)dstore/document/<id>/<name>.pdf. Other documents on the page
(e.g. a summer-school guide) are excluded by name.

Writes school_job_posts/school_id_1699_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1699_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1699
SCHOOL_NAME = 'Eötvös Loránd University'
CAREERS_LINK = 'https://www.elte.hu/en/work-opportunities'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://(?:www\.)?elte\.hu/(?:en/)?dstore/document/\d+/[^?#]+\.pdf', re.I)
NOT_A_POSTING_RE = re.compile(r'guide|summer|brochure|handbook', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True):
        if not NOT_A_POSTING_RE.search(url) and url not in links:
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
