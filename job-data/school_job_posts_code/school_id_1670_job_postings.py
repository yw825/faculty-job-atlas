"""
Job postings scraper for school_id 1670 - Aalto University (Finland)
ATS platform: own website
Careers link: https://www.aalto.fi/en/open-positions?sort_by=created&field_unit_target_id=All

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Aalto University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is /en/open-positions/<slug>; the listing paginates
(?page=N) and is walked until a page adds nothing.

Writes school_job_posts/school_id_1670_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1670_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1670
SCHOOL_NAME = 'Aalto University'
CAREERS_LINK = 'https://www.aalto.fi/en/open-positions?sort_by=created&field_unit_target_id=All'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.aalto\.fi/en/open-positions/[^/?#]+$', re.I)


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE, first_page=0)   # Drupal: page=0 is the first page


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
