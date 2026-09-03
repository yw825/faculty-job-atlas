"""
Job info scraper for school_id 1763 - University of Birmingham (United Kingdom)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://edzz.fa.em3.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_6001/jobs?lastSelectedFacet=CATEGORIES&selectedCategoriesFacet=300000002904064

Oracle Cloud HCM's listing API already returns title/department/description/
deadline for every posting in one call -- job_info_lib.fetch_oracle_bulk
reuses that instead of visiting each posting page individually.

Reads posting URLs from school_id_1763_job_postings.checkpoint (this
school's job_postings run) and classifies each one (position_type, job_term,
department_or_school, area_key_words, deadline_of_application,
position_start_date, job_title_in_post) with job_info_lib's rule-based
English-language classifier. Writes school_job_info/school_id_1763_job_info.csv.
Checkpointed to school_id_1763_job_info.checkpoint next to this script --
kill-and-resume, per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1763
SCHOOL_NAME = 'University of Birmingham'
CAREERS_LINK = 'https://edzz.fa.em3.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_6001/jobs?lastSelectedFacet=CATEGORIES&selectedCategoriesFacet=300000002904064'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, f'..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def main():
    result = jinfo.run_school_job_info_bulk(SCHOOL_ID, CAREERS_LINK, PLATFORM,
                                             JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
