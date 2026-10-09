"""
Job info scraper for school_id 1708 - Bocconi University (Italy)
ATS platform: own website
Careers link: https://jobmarket.unibocconi.eu/

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Bocconi University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: fetch_detail reads the call's row (position, department, sector,
deadline) and the English position-details PDF.

Reads posting URLs from school_id_1708_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1708_job_info.csv. Checkpointed to
school_id_1708_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1708
SCHOOL_NAME = 'Bocconi University'
CAREERS_LINK = 'https://jobmarket.unibocconi.eu/'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """The call's row on jobmarket.unibocconi.eu/?id=N gives the position,
    department, scientific sector and deadline; the description is the
    English "Position Details" PDF when there is one, else the "Job opening"
    PDF (the official notice, often Italian)."""
    import re
    from bs4 import BeautifulSoup
    # The main table, not the call's own ?id page: only the main table's row
    # carries the position ("Assistant Professor").
    call_id = url.rsplit('=', 1)[-1]
    tr = None
    for page in (CAREERS_LINK, url):
        status, html = jinfo.jlib.fetch_static(page, timeout=40)
        if status == 200:
            tr = BeautifulSoup(html, 'html.parser').find('tr', id=call_id)
            if tr is not None:
                break
    if tr is None:
        raise RuntimeError('call row not found')
    nxt = tr.find_next_sibling('tr')
    cells = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
    lines = [d.get_text(' ', strip=True) for d in tr.find_all('td')[1].find_all('div')] if len(cells) > 1 else []
    rank = lines[0] if lines and not lines[0].startswith('Dept') else 'Faculty position'
    dept = next((x for x in lines[1:] if x.startswith('Dept')), '')
    sector = cells[2] if len(cells) > 2 else ''
    sector = ', '.join(dict.fromkeys(x.strip() for x in sector.split(',') if x.strip()))
    title = ', '.join(x for x in (rank, dept, sector.title() if sector.isupper() else sector) if x)
    head = []
    m = re.search(r'Deadline\s*(\d{2}/\d{2}/\d{4})', cells[0] if cells else '')
    if m:
        head.append('Closing Date: ' + m[1])
    m = re.search(r'(?:Publication|G\.U\.[^0-9]*\d+)\s*(\d{2}/\d{2}/\d{4})', cells[0] if cells else '')
    if m:
        head.append('Posted Date: ' + m[1])
    if dept:
        head.append('Department: ' + dept.replace('Dept. ', ''))
    pdfs = {a.get_text(strip=True): a['href'] for a in (nxt.find_all('a', href=True) if nxt else [])}
    body = ''
    for label in ('Position Details (ENG)', 'Job opening', 'Position Details (ITA)'):
        if label in pdfs:
            try:
                body = jinfo.fetch_detail_pdf(pdfs[label])[1]
                break
            except Exception:
                continue
    return title[:250], (' '.join(head) + ' ' + re.sub(r'\s+', ' ', body))[:20000]


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
