"""
Job postings scraper for school_id 1667 - University of Copenhagen (Denmark)
ATS platform: own website
Careers link: https://jobportal.ku.dk/tenure-track/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Copenhagen; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each tenure-track opening is jobportal.ku.dk/tenure-track/?show=<id>.

Writes school_job_posts/school_id_1667_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1667_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1667
SCHOOL_NAME = 'University of Copenhagen'
CAREERS_LINK = 'https://jobportal.ku.dk/tenure-track/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://jobportal\.ku\.dk/tenure-track/\?show=\d+$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
