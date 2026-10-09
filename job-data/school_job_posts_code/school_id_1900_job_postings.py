"""
Job postings scraper for school_id 1900 - NHH Norwegian School of Economics (Norway)
Careers link: https://www.nhh.no/en/about-nhh/vacant-positions/

Writes school_job_posts/school_id_1900_job_posts.csv. Checkpointed to
school_id_1900_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Kept: Jobbnorge job pages only (not the page itself or its share buttons).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1900
SCHOOL_NAME = 'NHH Norwegian School of Economics'
CAREERS_LINK = 'https://www.nhh.no/en/about-nhh/vacant-positions/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def _page_links():
    """Job word first, repeated URL shape second (lib.scrape_listing)."""
    return lib.scrape_listing(CAREERS_LINK)


POSTING_RE = re.compile(r'jobbnorge\.no/.*/(?:job|stilling)/\d+')


def find_links():
    """Only real postings: the page also links its menus, careers home and
    share buttons, which were being stored as jobs."""
    return [u for u in _page_links() if POSTING_RE.search(u)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
