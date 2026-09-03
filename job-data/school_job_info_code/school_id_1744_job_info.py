"""
Job info scraper for school_id 1744 - IE University (Spain)
ATS platform: iCIMS
Careers link: https://careers-ieedu.icims.com/jobs/search?ss=1

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if IE University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

Default: render the page, take the first heading (or <title>) as the job
title and the page's visible text as the description.

Reads posting URLs from school_id_1744_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1744_job_info.csv. Checkpointed to
school_id_1744_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1744
SCHOOL_NAME = 'IE University'
CAREERS_LINK = 'https://careers-ieedu.icims.com/jobs/search?ss=1'
ATS_PLATFORM = 'iCIMS'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """CUSTOMIZED (confirmed live): same nested-iframe trap that broke this
    school's LISTING scrape -- page.content() returns only the top
    document, whose visible headings are cookie/branding chrome, so all 66
    postings were recorded with the title "Privacy Policy". The posting
    itself lives in page.frames[1], and that frame only renders real
    content on a SECOND navigation (the first trips a "Please Enable
    Cookies to Continue" gate). The frame's <title> carries the job title
    with a " | Careers at <city>" suffix to strip.
    """
    from bs4 import BeautifulSoup

    browser = jinfo.get_browser()
    if browser is None:
        raise RuntimeError('playwright unavailable')
    page = browser.new_page(user_agent=jlib_ua())
    try:
        for _ in range(2):
            page.goto(url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
        frame = page.frames[1] if len(page.frames) > 1 else page.frames[0]
        soup = BeautifulSoup(frame.content(), 'html.parser')
    finally:
        page.close()

    raw_title = (soup.title.string or '').strip() if soup.title else ''
    # "<Job title> in <City> | Careers at <City>" -- take the city from the
    # suffix, then drop the matching " in <City>" the title repeats, so the
    # location doesn't end up as the job title or as an area keyword
    # (confirmed live: "Madrid" and "Student Experience in Madrid" were
    # being recorded as area_key_words).
    city = ''
    m = re.search(r'\|\s*Careers at\s+(.+?)\s*$', raw_title)
    if m:
        city = m.group(1).strip()
    title = re.sub(r'\s*\|\s*Careers at .*$', '', raw_title).strip()
    if city:
        title = re.sub(r'\s+in\s+' + re.escape(city) + r'\s*$', '', title).strip()
    return title, soup.get_text(' ', strip=True)


def jlib_ua():
    import job_postings_lib as jlib
    return jlib.UA


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
