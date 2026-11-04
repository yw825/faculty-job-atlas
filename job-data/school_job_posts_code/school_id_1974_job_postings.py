"""
Job postings scraper for school_id 1974 - The University of Tennessee Health Science Center (US)
ATS platform: Oracle
Careers link: https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?selectedCategoriesFacet=300000024535357&selectedOrganizationsFacet=300000014275287

UT System Oracle site (CX_1), category Faculty + business unit UT Health Science Center.

Writes school_job_posts/school_id_1974_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1974_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1974
SCHOOL_NAME = "The University of Tennessee Health Science Center"
CAREERS_LINK = 'https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?selectedCategoriesFacet=300000024535357&selectedOrganizationsFacet=300000014275287'
ATS_PLATFORM = 'Oracle'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_oracle_link(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
