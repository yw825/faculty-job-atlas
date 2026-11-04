"""
Job postings scraper for school_id 1957 - University of Oklahoma-Health Sciences Center (US)
ATS platform: Interfolio
Careers link: https://apply.interfolio.com/46259/positions

OU Health Campus faculty Interfolio board; Tulsa-located postings belong to OU-Tulsa (1958).

Writes school_job_posts/school_id_1957_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1957_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1957
SCHOOL_NAME = "University of Oklahoma-Health Sciences Center"
CAREERS_LINK = 'https://apply.interfolio.com/46259/positions'
ATS_PLATFORM = 'Interfolio'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_interfolio_located([CAREERS_LINK], exclude=r'(?i)tulsa')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
