"""
Job postings scraper for school_id 1966 - Lackawanna College (US)
ATS platform: ADP
Careers link: https://www.lackawanna.edu/about/employment/available-positions/

The positions page lists Lackawanna's ADP Workforce Now board (Peirce College merged into Lackawanna).

Writes school_job_posts/school_id_1966_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1966_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1966
SCHOOL_NAME = "Lackawanna College"
CAREERS_LINK = 'https://www.lackawanna.edu/about/employment/available-positions/'
ATS_PLATFORM = 'ADP'

BOARD = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=9d114fa5-887f-4687-9b71-ee538589a4bb&ccId=19000101_000001&lang=en_US'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_adp(BOARD)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
