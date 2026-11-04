"""
Job info scraper for school_id 904 - University of Nevada-Reno (US)
ATS platform: Workday
Careers link: https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=dddb2e55fbdf018c7a8b5718563592a1&locations=dddb2e55fbdf014cadc74f18563588a1&locations=dddb2e55fbdf01a639587d185635c4a1&locations=dddb2e55fbdf01c792a08f185635dda1&locations=dddb2e55fbdf013f6327481856357ea1&locations=dddb2e55fbdf010fb9a479185635bfa1&locations=dddb2e55fbdf014d1b1788185635d3a1&locations=dddb2e55fbdf01d2538e6e185635b0a1&locations=dddb2e55fbdf010679085f1856359ca1&locations=dddb2e55fbdf01e12d6e4418563579a1&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313

Reads posting URLs from school_id_904_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_904_job_info.csv. Checkpointed to
school_id_904_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 904
SCHOOL_NAME = 'University of Nevada-Reno'
CAREERS_LINK = 'https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=dddb2e55fbdf018c7a8b5718563592a1&locations=dddb2e55fbdf014cadc74f18563588a1&locations=dddb2e55fbdf01a639587d185635c4a1&locations=dddb2e55fbdf01c792a08f185635dda1&locations=dddb2e55fbdf013f6327481856357ea1&locations=dddb2e55fbdf010fb9a479185635bfa1&locations=dddb2e55fbdf014d1b1788185635d3a1&locations=dddb2e55fbdf01d2538e6e185635b0a1&locations=dddb2e55fbdf010679085f1856359ca1&locations=dddb2e55fbdf01e12d6e4418563579a1&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313'
ATS_PLATFORM = 'Workday'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """Workday posting, from the board's own job service."""
    return jinfo.fetch_detail_workday(url)


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
