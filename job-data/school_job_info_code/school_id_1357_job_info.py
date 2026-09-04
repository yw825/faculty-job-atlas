"""
Job info scraper for school_id 1357 - The University of Tennessee Southern (US)
ATS platform: Oracle Cloud HCM
Careers link: https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?location=Pulaski%2C+TN%2C+United+States&locationId=300000010467855&locationLevel=city&mode=location&radius=25&radiusUnit=MI

Reads posting URLs from school_id_1357_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Every posting's title, department and description come back from ONE oracle API call (BULK_ADAPTERS), not a visit per posting.

area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_1357_job_info.csv. Checkpointed to
school_id_1357_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1357
SCHOOL_NAME = 'The University of Tennessee Southern'
CAREERS_LINK = 'https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?location=Pulaski%2C+TN%2C+United+States&locationId=300000010467855&locationLevel=city&mode=location&radius=25&radiusUnit=MI'
ATS_PLATFORM = 'Oracle Cloud HCM'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')



def main():
    result = jinfo.run_school_job_info_bulk(SCHOOL_ID, CAREERS_LINK, 'oracle',
                                            JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,
                                            use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
