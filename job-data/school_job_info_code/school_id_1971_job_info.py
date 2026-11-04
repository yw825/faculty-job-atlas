"""
Job info scraper for school_id 1971 - The University of Texas Health Science Center at Houston (US)
ATS platform: Taleo
Careers link: https://careers.uth.tmc.edu/us/en/c/faculty-physicians-jobs

Reads posting URLs from school_id_1971_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Writes school_job_info/school_id_1971_job_info.csv. Checkpointed to
school_id_1971_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1971
SCHOOL_NAME = "The University of Texas Health Science Center at Houston"
CAREERS_LINK = 'https://careers.uth.tmc.edu/us/en/c/faculty-physicians-jobs'
ATS_PLATFORM = 'Taleo'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """Default: render the page, take the first heading (or <title>) as the job
title and the page's visible text as the description."""
    return jinfo.fetch_detail_generic(url)


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
