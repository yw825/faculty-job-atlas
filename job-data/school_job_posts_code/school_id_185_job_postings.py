"""
Job postings scraper for school_id 185 - Trinity College (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://trincoll.peopleadmin.com/postings/search

Trinity College runs on a shared ATS platform -- every school on oracle uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_185_job_posts.csv (school_id, post_link).
Checkpointed to school_id_185_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Trinity's Oracle board (the audit's link) lists staff jobs only; faculty
openings are on its PeopleAdmin board, trincoll.peopleadmin.com. Both are read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 185
SCHOOL_NAME = 'Trinity College'
CAREERS_LINK = 'https://trincoll.peopleadmin.com/postings/search'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

STAFF_BOARD = 'https://trincore-ibvxjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return list(dict.fromkeys(lib.scrape_peopleadmin_search(CAREERS_LINK) + lib.scrape_oracle_link(STAFF_BOARD)))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
