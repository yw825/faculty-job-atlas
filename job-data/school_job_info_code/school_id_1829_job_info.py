"""
Job info scraper for school_id 1829 - Massey University (New Zealand)
ATS platform: own website
Careers link: https://massey.t1cloud.com/T1Default/CiAnywhere/Web/MASSEY/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Massey University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: a posting is a card (#<Reference>) on the board; fetch_detail reads
the card -- the advertisement itself is not visible to guests.

Reads posting URLs from school_id_1829_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1829_job_info.csv. Checkpointed to
school_id_1829_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1829
SCHOOL_NAME = 'Massey University'
CAREERS_LINK = 'https://massey.t1cloud.com/T1Default/CiAnywhere/Web/MASSEY/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


_CARDS = {}


def fetch_detail(url):
    """Title, unit, contract type, reference and closing date from the job's
    card on the board (rendered once per run). "19-Oct-2026 11:00 PM" is
    restated as Closing Date: 19/10/2026."""
    import datetime
    import importlib.util
    import re
    if not _CARDS:
        path = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.py')
        spec = importlib.util.spec_from_file_location('massey_postings', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for ref, title, text in mod.board_cards():
            _CARDS[ref] = (title, text)
    ref = url.rsplit('#', 1)[-1]
    if ref not in _CARDS:
        raise RuntimeError(f'{ref} no longer on the board')
    title, text = _CARDS[ref]
    lead = ''
    m = re.search(r'(\d{1,2}-[A-Za-z]{3}-\d{4})', text)
    if m:
        lead = 'Closing Date: ' + datetime.datetime.strptime(m[1], '%d-%b-%Y').strftime('%d/%m/%Y') + ' '
    unit = [f for f in text.split(' | ') if f not in (title, 'Massey University') and not re.search(r'\d{4}|^JR-|^(Ongoing|Fixed-Term|Casual)$', f)]
    if unit:
        lead += f'Department: {unit[0]} '
    return title[:250], f'{lead}{title}. Massey University. {text}'


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
