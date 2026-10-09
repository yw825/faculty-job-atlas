"""
Job info scraper for school_id 1715 - University of Luxembourg (Luxembourg)
ATS platform: own website
Careers link: https://www.uni.lu/en/about/work/explore-our-jobs/

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if University of Luxembourg's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: pages read through installed Chrome (CloudFront blocks the bundled browser).

Reads posting URLs from school_id_1715_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1715_job_info.csv. Checkpointed to
school_id_1715_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1715
SCHOOL_NAME = 'University of Luxembourg'
CAREERS_LINK = 'https://www.uni.lu/en/about/work/explore-our-jobs/'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """uni.lu sits behind CloudFront, which answers the bundled headless
    browser with "ERROR: The request could not be satisfied"; installed Chrome
    passes. Title = the page's h1."""
    import re
    from bs4 import BeautifulSoup
    import time
    # CloudFront starts answering 403 after a few quick page loads, so pages
    # are spaced out and a 403 is retried after a pause.
    title, html = '', ''
    for wait in (6, 45, 120):
        time.sleep(wait)
        page = jinfo.jlib.get_real_chrome().new_page()
        try:
            page.goto(url, timeout=90000)
            page.wait_for_timeout(4000)
            html = page.content()
        finally:
            page.close()
        h1 = BeautifulSoup(html, 'html.parser').find('h1')
        title = h1.get_text(' ', strip=True) if h1 else ''
        if title and not re.search(r'403 ERROR|could not be satisfied', title):
            break
    soup = BeautifulSoup(html, 'html.parser')
    if not title or re.search(r'403 ERROR|could not be satisfied', title):
        raise RuntimeError('blocked by CloudFront (403)')
    main = soup.find('main') or soup
    for tag in main(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    return title[:250], re.sub(r'\s+', ' ', main.get_text(' ', strip=True))[:20000]


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
