"""
Job postings scraper for school_id 1772 - London Business School
ATS platform: Interfolio
Careers link: https://apply.interfolio.com/18804/positions

jobsearch.london.edu is the school's STAFF board -- it returned twelve
professional-services roles (Lead Data Analyst, QA Engineer, Faculty HR
Adviser) and no academic posts at all. LBS advertises faculty positions on
Interfolio board 18804, which carries fourteen, including the Management
Science and Operations tenure-track post a user found on LinkedIn.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1772
SCHOOL_NAME = 'London Business School'
CAREERS_LINK = 'https://apply.interfolio.com/18804/positions'
ATS_PLATFORM = 'Interfolio'
PLATFORM = 'interfolio'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
