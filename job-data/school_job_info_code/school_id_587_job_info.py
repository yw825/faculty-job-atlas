"""
Job info scraper for school_id 587 - University of Maryland Global Campus (US)
ATS platform: own website
Careers link: https://careers.umgc.edu/jobs/

Reads posting URLs from school_id_587_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_587_job_info.csv. Checkpointed to
school_id_587_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 587
SCHOOL_NAME = 'University of Maryland Global Campus'
CAREERS_LINK = 'https://careers.umgc.edu/jobs/'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """UMGC job page; the job title is its last <h1> (the first is the site banner
    "UMGC Careers. Never Stop Learning." and the <title> is just
    "Jobs | UMGC Careers")."""
    from bs4 import BeautifulSoup
    status, html = jinfo.jlib.fetch_static(url, timeout=40)
    if status != 200:
        raise RuntimeError(f'page status={status}')
    soup = BeautifulSoup(html, 'html.parser')
    heads = [re.sub(r'\s+', ' ', h.get_text(' ', strip=True)) for h in soup.find_all('h1')]
    heads = [h for h in heads if h and not h.startswith('UMGC Careers')]
    title = heads[-1] if heads else ''
    if not title:
        raise RuntimeError('posting not on the page (closed?)')
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    return title[:250], re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))[:20000]


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
