"""
Job postings scraper for school_id 75 - Woodbury University (US)
ATS platform: own website
Careers link: https://recruiting.ultipro.com/WOO1008WBURY/JobBoard/c85e7610-e7f7-410f-85c6-c530dd8194e2/?q=&o=postedDateDesc

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Woodbury University; nothing here affects any
other school's script.

Link check (ok): 3 posting-shaped links found.

TUNED FIND_LINKS
The board is UKG/UltiPro (WOO1008WBURY); postings are read through the
shared UltiPro adapter as .../OpportunityDetail?opportunityId=<id>. On
2026-10-07 the board itself read "Showing 0 of 0 opportunities".

Writes school_job_posts/school_id_75_job_posts.csv (school_id, post_link).
Checkpointed to school_id_75_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 75
SCHOOL_NAME = 'Woodbury University'
CAREERS_LINK = 'https://recruiting.ultipro.com/WOO1008WBURY/JobBoard/c85e7610-e7f7-410f-85c6-c530dd8194e2/?q=&o=postedDateDesc'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_PATTERN = 'woodbury.edu/admissions/undergraduate-admission/<*>'


def find_links():
    return lib.scrape_ultipro(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
