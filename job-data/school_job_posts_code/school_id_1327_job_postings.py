"""
Job postings scraper for school_id 1327 - Tennessee Technological University
ATS platform: Oracle Recruiting Cloud (detected: oracle)
Careers link: https://fa-eygi-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1

Tennessee Technological University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 38 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
oracle school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_1327_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1327_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1327
SCHOOL_NAME = 'Tennessee Technological University'
CAREERS_LINK = 'https://fa-eygi-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1'
ATS_PLATFORM = 'Oracle Recruiting Cloud'
PLATFORM = 'oracle'

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
