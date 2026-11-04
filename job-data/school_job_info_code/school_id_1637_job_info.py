"""
Job info scraper for school_id 1637 - University of Windsor (Canada)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://efhc.fa.ca2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?sortBy=POSTING_DATES_DESC

University of Windsor runs on a shared ATS platform with a bulk info adapter --
job_info_lib.fetch_oracle_bulk gets title/department/description/
deadline for every posting in ONE call instead of visiting each posting
page individually (confirmed on Birmingham: the same listing call
job_postings_lib.scrape_oracle already uses for links also carries
these fields).

Reads posting URLs from school_id_1637_job_postings.checkpoint (this
school's job_postings run) and classifies each one (position_type,
job_term, department_or_school, area_key_words, deadline_of_application,
position_start_date, job_title_in_post). area_key_words combines a
rule-based primary keyword read off the title's own rank clause (e.g.
"Assistant Professor in X" -> "X") with supporting keywords -- by default
scored via local TF-IDF against this school's OTHER postings (no API
needed); pass use_llm=True below instead if you have ANTHROPIC_API_KEY
configured, for an LLM read of each description instead (higher quality,
not validated in the session that wrote this script -- no credentials
were available there).

Writes school_job_info/school_id_1637_job_info.csv. Checkpointed to
school_id_1637_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity for the fetch phase.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1637
SCHOOL_NAME = 'University of Windsor'
CAREERS_LINK = 'https://efhc.fa.ca2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?sortBy=POSTING_DATES_DESC'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def main():
    result = jinfo.run_school_job_info_bulk(SCHOOL_ID, CAREERS_LINK, PLATFORM,
                                             JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH, use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
