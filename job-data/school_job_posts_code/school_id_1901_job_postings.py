"""
Job postings scraper for school_id 1901 - IMD Business School (Switzerland)
Careers link: https://jobs.imd.org/search/

Writes school_job_posts/school_id_1901_job_posts.csv. Checkpointed to
school_id_1901_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1901
SCHOOL_NAME = 'IMD Business School'
CAREERS_LINK = 'https://jobs.imd.org/search/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    """Job word first, repeated URL shape second (lib.scrape_listing)."""
    return lib.scrape_listing(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
