"""
Job postings scraper for school_id 1636 - Wilfrid Laurier University (Canada)
ATS platform: own website
Careers link: https://careers.wlu.ca/go/Academic-Positions/505047/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Wilfrid Laurier University; nothing here affects any
other school's script.

TUNED FIND_LINKS
SAP SuccessFactors board: each posting is /job/<slug>/<numeric id>/.
lib.scrape_successfactors walks the listing's pages (it shows 20-25 at a
time and says "Showing 1 to 20 of N") and dedupes by job id.

Writes school_job_posts/school_id_1636_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1636_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1636
SCHOOL_NAME = 'Wilfrid Laurier University'
CAREERS_LINK = 'https://careers.wlu.ca/go/Academic-Positions/505047/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_successfactors(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
