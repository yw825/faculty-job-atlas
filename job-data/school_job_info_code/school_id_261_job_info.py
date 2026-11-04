"""
Job info scraper for school_id 261 - Florida State University (US)
ATS platform: own website
Careers link: https://jobs.omni.fsu.edu/psc/sprdhr_er/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U

Reads posting URLs from school_id_261_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_261_job_info.csv. Checkpointed to
school_id_261_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 261
SCHOOL_NAME = 'Florida State University'
CAREERS_LINK = 'https://jobs.omni.fsu.edu/psc/sprdhr_er/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """Rendered job page: "... Previous Job Job Title <title> Next Job Apply for Job Job ID <n> ..."."""
    import re
    from bs4 import BeautifulSoup
    html = jinfo.jlib.fetch_rendered(url, wait_ms=8000)
    if not html or jinfo.jlib.is_fetch_failure(html):
        raise RuntimeError(html or 'page did not render')
    text = re.sub(r'\s+', ' ', BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    m = re.search(r'Job Title\s+(.+?)\s+(?:Next Job|Apply for Job)', text) or re.search(r'Previous Job\s+(.+?)\s+(?:Next Job|Apply for Job)', text)
    if not m:
        raise RuntimeError('job description not shown (closed?)')
    return m.group(1).strip()[:250], text[text.find(m.group(1)):][:20000]


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
