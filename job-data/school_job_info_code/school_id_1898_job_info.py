"""
Job info scraper for school_id 1898 - CATÓLICA-LISBON School of Business & Economics (Portugal)
Careers link: https://clsbe.lisboa.ucp.pt/research/research-positions

Reads posting URLs from school_id_1898_job_postings.checkpoint and writes
school_job_info/school_id_1898_job_info.csv.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1898
SCHOOL_NAME = 'CATÓLICA-LISBON School of Business & Economics'
CAREERS_LINK = 'https://clsbe.lisboa.ucp.pt/research/research-positions'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """Title and deadline from the research-positions table row that links
    this PDF ("Assistant Professor in Quantitative Marketing", "October 1st,
    2026"); description from the PDF itself."""
    import re
    from bs4 import BeautifulSoup
    status, html = jinfo.jlib.fetch_static(CAREERS_LINK, timeout=40)
    title, lead = '', ''
    if status == 200:
        for row in BeautifulSoup(html, 'html.parser').find_all('tr'):
            a = row.find('a', href=True)
            if a and a['href'].split('/')[-1] == url.split('/')[-1]:
                cells = [c.get_text(' ', strip=True) for c in row.find_all('td')]
                title = re.sub(r'\s*Download PDF\s*$', '', cells[0]) if cells else ''
                if len(cells) >= 3:
                    lead = f'Deadline: {cells[-2]} '
                break
    pdf_title, text = jinfo.fetch_detail_pdf(url)
    return (title or pdf_title)[:250], (lead + re.sub(r'\s+', ' ', text))[:20000]


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
