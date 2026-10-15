"""
Job postings scraper for school_id 373 - DePaul University (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://apply.interfolio.com/32267/positions

DePaul University runs on a shared ATS platform -- every school on oracle uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_373_job_posts.csv (school_id, post_link).
Checkpointed to school_id_373_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to DePaul's Oracle board.
DePaul's Oracle board (the audit's link) carries staff jobs; its faculty
openings (130) are on Interfolio board 32267. Both are read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 373
SCHOOL_NAME = 'DePaul University'
CAREERS_LINK = 'https://apply.interfolio.com/32267/positions'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

STAFF_BOARD = 'https://ekze.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return list(dict.fromkeys(lib.scrape_interfolio(CAREERS_LINK) + lib.PLATFORM_ADAPTERS['oracle'](STAFF_BOARD, SCHOOL_NAME)))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
