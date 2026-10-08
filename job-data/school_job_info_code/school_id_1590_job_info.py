"""
Job info scraper for school_id 1590 - University of the Fraser Valley (Canada)
ATS platform: Njoyn
Careers link: https://ufv.njoyn.com/CL3/xweb/Xweb.asp?page=joblisting&CLID=56144

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if University of the Fraser Valley's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

Default: render the page, take the first heading (or <title>) as the job
title and the page's visible text as the description.

Reads posting URLs from school_id_1590_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1590_job_info.csv. Checkpointed to
school_id_1590_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1590
SCHOOL_NAME = 'University of the Fraser Valley'
CAREERS_LINK = 'https://ufv.njoyn.com/CL3/xweb/Xweb.asp?page=joblisting&CLID=56144'
ATS_PLATFORM = 'Njoyn'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


_POSTINGS = None


def fetch_detail(url):
    """CUSTOMIZED: Njoyn job pages sit behind a Radware bot wall that blocks
    headless browsers, so each page is read in the installed Chrome (the
    postings script's njoyn_page, which also spaces requests out)."""
    global _POSTINGS
    import re
    from bs4 import BeautifulSoup
    if _POSTINGS is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'njoyn_postings', os.path.join(HERE, '..', 'school_job_posts_code',
                                           f'school_id_{SCHOOL_ID}_job_postings.py'))
        _POSTINGS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_POSTINGS)
    soup = BeautifulSoup(_POSTINGS.njoyn_page(url), 'html.parser')
    generic = re.compile(r'(?i)career|job postings?')
    candidates = []
    kw = soup.find('meta', attrs={'name': 'keywords'})
    if kw and kw.get('content'):
        candidates.append(kw['content'].split(' - ', 2)[-1])  # strip only "<School> - Careers - "
    og = soup.find('meta', attrs={'property': 'og:title'})
    if og and og.get('content'):
        candidates.append(og['content'])
    candidates += [h.get_text(' ', strip=True) for h in soup.find_all('h1')]
    title = next((c.strip() for c in candidates if c and c.strip() and not generic.search(c)), '')
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    text = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
    return title[:200], text[:20000]


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
