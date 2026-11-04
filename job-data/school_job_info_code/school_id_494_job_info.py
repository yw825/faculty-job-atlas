"""
Job info scraper for school_id 494 - Transylvania University (US)
ATS platform: own website
Careers link: https://www.transy.edu/employment-opportunities/

Reads posting URLs from school_id_494_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_494_job_info.csv. Checkpointed to
school_id_494_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 494
SCHOOL_NAME = 'Transylvania University'
CAREERS_LINK = 'https://www.transy.edu/employment-opportunities/'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """a Recruiterbox opening shown inside the employment page (address = page + #op-<id>-<slug>)."""
    page = jinfo.jlib.get_browser().new_page(user_agent=jinfo.jlib.UA)
    try:
        page.goto(url, timeout=60000, wait_until='domcontentloaded')
        page.wait_for_timeout(9000)
        head = page.query_selector('.rbox-job-title')
        box = page.query_selector('.rbox-opening-detail')
        title = re.sub(r'\s+', ' ', head.inner_text()).strip() if head else ''
        text = re.sub(r'\s+', ' ', box.inner_text()) if box else ''
    finally:
        page.close()
    if not title or len(text) < 200:
        raise RuntimeError('opening no longer listed')
    return title[:250], text[:20000]


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
