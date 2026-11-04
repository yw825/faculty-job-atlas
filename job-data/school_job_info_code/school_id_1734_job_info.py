"""
Job info scraper for school_id 1734 - Universidade de Lisboa (Portugal)
ATS platform: own website
Careers link: https://www.ulisboa.pt/en/info/recruitment

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Universidade de Lisboa's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: fetch_detail reads the call page's fields (category, area, unit,
deadline) and gives an English title.

Reads posting URLs from school_id_1734_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1734_job_info.csv. Checkpointed to
school_id_1734_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1734
SCHOOL_NAME = 'Universidade de Lisboa'
CAREERS_LINK = 'https://www.ulisboa.pt/en/info/recruitment'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """A ULisboa call page: the h1 is the Portuguese edital title ("Edital
    n.º 1236/2026 concurso para dois professores catedráticos, na área
    disciplinar de Psicologia Aplicada"); the English Professional Category
    and Unit fields give "Full Professor, Psicologia Aplicada - Faculty of
    Psychology". The Deadline is restated as a Closing Date."""
    import re
    from bs4 import BeautifulSoup
    status, html = jinfo.jlib.fetch_static(url, timeout=40)
    if status != 200:
        raise RuntimeError(f'call page status={status}')
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup
    for tag in main(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    text = re.sub(r'\s+', ' ', main.get_text(' ', strip=True))
    stop = r'(?= (?:Código|Professional Category|N\.º de Vagas|Career|Deadline|Unit|Tipo de Oferta|Target|Characterisation|Perfil|Anexos)\b)'
    field = lambda k: (re.search(k + r' (.+?)' + stop, text) or [None, ''])[1].strip()
    h1 = soup.find('h1')
    head = re.sub(r'\s+', ' ', h1.get_text(' ', strip=True)) if h1 else ''
    area = (re.search(r'(?i)área(?: disciplinar)? (?:de|em) (.+)$', head) or [None, ''])[1].strip(' .')
    area = re.sub(r'\s*\(exec_senten[çc]a\)', '', area)
    ranks = [(r'catedr', 'Full Professor'), (r'associad', 'Associate Professor'), (r'auxiliar', 'Assistant Professor'),
             (r'coordenador', 'Coordinating Professor'), (r'adjunt', 'Adjunct Professor'), (r'investigador', 'Researcher')]
    rank = field('Professional Category') or next((en for pt, en in ranks if re.search(r'(?i)professor(?:es)? ' + pt + '|' + pt + r'\w* ', head)), 'Faculty position')
    unit = field('Unit')
    title = rank + (f', {area}' if area else '') + (f' - {unit}' if unit else '')
    deadline = field('Deadline')
    lead = (f'Closing Date: {deadline} ' if re.match(r'\d{2}/\d{2}/\d{4}', deadline) else '') + (f'Department: {unit} ' if unit else '')
    return title[:250], (lead + head + ' ' + text)[:20000]


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
