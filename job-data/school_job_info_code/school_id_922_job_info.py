"""
Job info scraper for school_id 922 - St. Joseph's University-New York (US)
ATS platform: own website
Careers link: https://www.sjny.edu/employment

Reads posting URLs from school_id_922_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_922_job_info.csv. Checkpointed to
school_id_922_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 922
SCHOOL_NAME = 'St. Joseph\'s University-New York'
CAREERS_LINK = 'https://www.sjny.edu/employment'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """The site sits behind Cloudflare's automatic check ("Just a moment..."), which
the headless browser often does not pass; real Chrome passes it on its own
(nothing is solved). The job title is the page's h1."""
    from bs4 import BeautifulSoup
    html = jinfo.jlib.fetch_real_chrome(url)
    soup = BeautifulSoup(html or '', 'html.parser')
    h1 = soup.find('h1')
    title = h1.get_text(' ', strip=True) if h1 else ''
    if not title or 'Just a moment' in (soup.title.get_text() if soup.title else ''):
        raise RuntimeError('posting did not load (bot check or closed)')
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
