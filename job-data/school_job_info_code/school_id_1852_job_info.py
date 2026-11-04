"""
Job info scraper for school_id 1852 - Macao University of Science and Technology (Macau)
ATS platform: own website
Careers link: https://careers.must.edu.mo/recruitment-latest?locale=en_US

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Macao University of Science and Technology's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: pages are a JavaScript app; read rendered, title before 職位編碼.

Reads posting URLs from school_id_1852_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1852_job_info.csv. Checkpointed to
school_id_1852_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1852
SCHOOL_NAME = 'Macao University of Science and Technology'
CAREERS_LINK = 'https://careers.must.edu.mo/recruitment-latest?locale=en_US'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """MUST's posting page is a JavaScript app (the static HTML is only the site
    name). Rendered, the title sits between the 登入/註冊 links and the
    職位編碼 (position code) field; 招聘部門 is the department."""
    import re
    html = jinfo.jlib.fetch_rendered(url, wait_ms=6000)
    if not html or jinfo.jlib.is_fetch_failure(html):
        raise RuntimeError(html or 'page did not render')
    from bs4 import BeautifulSoup
    text = re.sub(r'\s+', ' ', BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    m = re.search(r'註冊\s+(.+?)\s+職位編碼', text)
    if not m:
        raise RuntimeError('posting not shown (closed?)')
    dept = re.search(r'招聘部門\s+(\S+)', text)
    lead = f'Department: {dept.group(1)} ' if dept else ''
    title = m.group(1).strip()
    if dept and re.match(r'(?i)^[\s/]*(?:(?:assistant|associate|full|distinguished|chair)\s+)?professor(?:[\s/]+(?:(?:assistant|associate|full)\s+)?professor)*\s*$', title):
        title = f'{title} - {dept.group(1)}'
    return title[:250], (lead + text[m.start(1):])[:20000]


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
