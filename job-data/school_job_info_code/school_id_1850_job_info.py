"""
Job info scraper for school_id 1850 - Macao Polytechnic University (Macau)
ATS platform: own website
Careers link: https://earth.ipm.edu.mo/store/en/pre/notification/page/home

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Macao Polytechnic University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: title from the call's box on the recruitment page, text from its PDF.

Reads posting URLs from school_id_1850_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1850_job_info.csv. Checkpointed to
school_id_1850_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1850
SCHOOL_NAME = 'Macao Polytechnic University'
CAREERS_LINK = 'https://earth.ipm.edu.mo/store/en/pre/notification/page/home'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """The call's title ("Recruitment of 8 Full-time Lecturers (area of ...)")
    from its box in the Academic Staff tab; description from the notice PDF."""
    import re
    from bs4 import BeautifulSoup
    title = ''
    status, html = jinfo.jlib.fetch_static(CAREERS_LINK, timeout=40)
    if status == 200:
        tab = BeautifulSoup(html, 'html.parser').find(id='tab-aca')
        for box in (tab.select('.box') if tab else []):
            if any(a['href'].split('/')[-1] == url.split('/')[-1] for a in box.find_all('a', href=True)):
                title = box.select_one('.box-title').get_text(' ', strip=True)
                break
    pdf_title, text = jinfo.fetch_detail_pdf(url)
    title = re.sub(r'_Job Vacancies at .*?(?=\(|$)', ' ', title or pdf_title)
    return re.sub(r'\s+', ' ', title).strip()[:250], re.sub(r'\s+', ' ', text)[:20000]


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
