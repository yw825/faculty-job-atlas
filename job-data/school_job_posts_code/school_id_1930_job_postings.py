"""
Job postings scraper for school_id 1930 - University of Minnesota-Rochester (US)
ATS platform: PeopleSoft (UMN system)
Careers link: https://hr.myu.umn.edu/psc/hrprd/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U

The University of Minnesota's campuses share one PeopleSoft board that shows
at most 300 of its 700+ jobs; its Faculty and Professionals-in-Training
(postdoc) job types are ticked and the rows whose Location is Rochester kept.

Writes school_job_posts/school_id_1930_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1930_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1930
SCHOOL_NAME = 'University of Minnesota-Rochester'
CAREERS_LINK = 'https://hr.myu.umn.edu/psc/hrprd/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U'
ATS_PLATFORM = 'PeopleSoft (UMN system)'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_umn_campus('Rochester')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
