"""
Job info scraper for school_id 1972 - The University of Texas Health Science Center at San Antonio (US)
ATS platform: Taleo
Careers link: https://uthscsa.referrals.selectminds.com/faculty

Reads posting URLs from school_id_1972_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Writes school_job_info/school_id_1972_job_info.csv. Checkpointed to
school_id_1972_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1972
SCHOOL_NAME = "The University of Texas Health Science Center at San Antonio"
CAREERS_LINK = 'https://uthscsa.referrals.selectminds.com/faculty'
ATS_PLATFORM = 'Taleo'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """the page title reads "<job>s+-s+UT Health San Antonio Careers..."; the full title is taken there."""
    return jinfo.fetch_detail_title_before(url, r'\s+-\s+UT Health San Antonio Careers')


def main():
    result = jinfo.run_school_job_info(SCHOOL_ID, JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,
                                       fetch_detail_fn=fetch_detail, use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
