"""
Job info scraper for school_id 1935 - University of North Carolina-School of the Arts (US)
ATS platform: PeopleAdmin
Careers link: https://employment.uncsa.edu/postings/search?query=&query_position_type_id%5B%5D=3&commit=Search

Reads posting URLs from school_id_1935_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Writes school_job_info/school_id_1935_job_info.csv. Checkpointed to
school_id_1935_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1935
SCHOOL_NAME = 'University of North Carolina-School of the Arts'
CAREERS_LINK = 'https://employment.uncsa.edu/postings/search?query=&query_position_type_id%5B%5D=3&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """PeopleAdmin posting; the title is the last part of the page's <title> text."""
    return jinfo.fetch_detail_peopleadmin(url)


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
