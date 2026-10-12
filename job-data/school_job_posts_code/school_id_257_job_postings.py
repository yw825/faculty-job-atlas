"""
Job postings scraper for school_id 257 - Flagler College
ATS platform: Interfolio (detected: interfolio)
Careers link: https://fa-ewbi-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?mode=location

Flagler College runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_interfolio adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 4 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
interfolio school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_257_job_posts.csv (school_id, post_link).
Checkpointed to school_id_257_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to the school's Oracle Recruiting board,
read through Oracle's public REST service (lib.scrape_oracle_rest).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 257
SCHOOL_NAME = 'Flagler College'
CAREERS_LINK = 'https://fa-ewbi-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?mode=location'
ATS_PLATFORM = 'Interfolio'
PLATFORM = 'interfolio'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_oracle_rest('https://fa-ewbi-saasfaprod1.fa.ocs.oraclecloud.com', 'CX_1')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
