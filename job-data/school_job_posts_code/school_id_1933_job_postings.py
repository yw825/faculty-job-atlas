"""
Job postings scraper for school_id 1933 - University of Montana-Helena College (US)
ATS platform: NEOGOV
Careers link: https://www.schooljobs.com/careers/ummissoula/helenacollege

Helena College's folder on the University of Montana NEOGOV board.

Writes school_job_posts/school_id_1933_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1933_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1933
SCHOOL_NAME = 'University of Montana-Helena College'
CAREERS_LINK = 'https://www.schooljobs.com/careers/ummissoula/helenacollege'
ATS_PLATFORM = 'NEOGOV'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [j['url'] for j in lib.neogov_jobs('ummissoula', 'helenacollege')]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
