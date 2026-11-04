"""
Job info scraper for school_id 1733 - Universidade de Coimbra (Portugal)
ATS platform: own website
Careers link: https://www.apply.uc.pt/

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if Universidade de Coimbra's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

TUNED: fetch_detail builds the call from its UC Apply record (rank, area,
sub-area, seats, application dates, contract type).

Reads posting URLs from school_id_1733_job_postings.checkpoint (this
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

Writes school_job_info/school_id_1733_job_info.csv. Checkpointed to
school_id_1733_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1733
SCHOOL_NAME = 'Universidade de Coimbra'
CAREERS_LINK = 'https://www.apply.uc.pt/'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    """The call's UC Apply record (the procedure page is a JavaScript app):
    "Full Professor: Chemistry / Organic Chemistry, ..." plus the opening
    and closing dates, seats and contract terms."""
    import re
    key = url.rstrip('/').rsplit('/', 1)[-1]
    rec = jinfo.jlib.uc_apply_calls().get(key)
    if rec is None:
        raise RuntimeError('call not in UC Apply search')
    rank = (rec.get('professional_category_key') or '').replace('_', ' ').title() or 'Faculty position'
    area = re.sub(r'\s+', ' ', (rec.get('area') or {}).get('en') or (rec.get('area') or {}).get('pt') or '').strip()
    sub = re.sub(r'\s+', ' ', (rec.get('sub_area') or {}).get('en') or '').strip()
    if sub.strip(' -./').lower() in ('', 'n/a', 'na', 'n.a', '---', area.lower()):
        sub = ''
    title = f'{rank}: {area}' + (f' / {sub}' if sub else '')
    fmt = lambda d: '/'.join(reversed(d.split('-'))) if d else ''
    parts = []
    if rec.get('applications_end'):
        parts.append('Closing Date: ' + fmt(rec['applications_end']))
    if rec.get('applications_start'):
        parts.append('Applications open: ' + fmt(rec['applications_start']))
    if rec.get('publish_date'):
        parts.append('Posted Date: ' + fmt(rec['publish_date']))
    parts.append(f"Reference: {rec.get('prefix') or ''}{rec.get('code') or ''}")
    parts.append(f"Positions: {rec.get('number_of_seats') or 1}")
    parts.append(f"Contract: {(rec.get('term_type') or '').replace('_', ' ')}; competition: {rec.get('category_type') or ''}")
    parts.append(f"Universidade de Coimbra -- {rank} in {area}" + (f' ({sub})' if sub else '') + '.')
    return title[:250], ' '.join(parts)


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
