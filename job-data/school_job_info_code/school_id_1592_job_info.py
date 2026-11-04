"""
Job info scraper for school_id 1592 - Thompson Rivers University (Canada)
ATS platform: HRSmart
Careers link: https://tru.hua.hrsmart.com/hr/ats/JobSearch/search

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Thompson Rivers University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

Default: render the page, take the first heading (or <title>) as the job
title and the page's visible text as the description.

Reads posting URLs from school_id_1592_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1592_job_info.csv. Checkpointed to
school_id_1592_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1592
SCHOOL_NAME = 'Thompson Rivers University'
CAREERS_LINK = 'https://tru.hua.hrsmart.com/hr/ats/JobSearch/search'
ATS_PLATFORM = 'HRSmart'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """CUSTOMIZED (confirmed live): HRSmart gives every posting page the
    same generic <h1> "Job Details" and the same <title> "Current
    Opportunities: Thompson Rivers University", so the generic picker
    recorded "Job Details" as the title for all 182 postings. The real
    title is the <h2> ("Sessional - Faculty (AUTO 1500, 1900, 2000) -
    (02050.11976)"). Body text comes from <main>, which excludes the site
    chrome around it.
    """
    from bs4 import BeautifulSoup

    html = jinfo.fetch_rendered(url, wait_ms=4000)
    if jinfo.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')

    text = soup.get_text(' ', strip=True)
    # 44 of the 182 postings are internal-only and render a login wall
    # instead of the job ("Error: Login is required to see these job
    # details."). Raising here records them as errors, which keeps them OUT
    # of the CSV entirely -- previously they became rows with a blank title,
    # which is worse than not listing them: they aren't postings anyone
    # outside TRU can read or apply to.
    if 'Login is required to see these job details' in text:
        raise RuntimeError('internal-only posting: login required')

    h2 = soup.find('h2')
    title = h2.get_text(' ', strip=True) if h2 else ''

    parts = [e.get_text(' ', strip=True) for e in soup.select('main, form')]  # noqa: E501
    description = max(parts, key=len, default='') if parts else ''
    extra = ' '.join(p for p in parts if p and p != description)
    description = (description + ' ' + extra).strip() or soup.get_text(' ', strip=True)
    return title, description


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
