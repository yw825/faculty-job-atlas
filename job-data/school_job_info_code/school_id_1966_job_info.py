"""
Job info scraper for school_id 1966 - Lackawanna College (US)
ATS platform: ADP
Careers link: https://www.lackawanna.edu/about/employment/available-positions/

Reads posting URLs from school_id_1966_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Writes school_job_info/school_id_1966_job_info.csv. Checkpointed to
school_id_1966_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1966
SCHOOL_NAME = "Lackawanna College"
CAREERS_LINK = 'https://www.lackawanna.edu/about/employment/available-positions/'
ATS_PLATFORM = 'ADP'
USE_LLM = False

BOARD = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=9d114fa5-887f-4687-9b71-ee538589a4bb&ccId=19000101_000001&lang=en_US'

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def main():
    # ADP's public API gives each requisition's title and description.
    result = jinfo.run_school_job_info_bulk(SCHOOL_ID, BOARD, 'adp',
                                            JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,
                                            use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
