"""
Job info scraper for school_id 802 - University of Mount Olive (US)
ATS platform: own website
Careers link: https://umo.edu/employment/

Reads posting URLs from school_id_802_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_802_job_info.csv. Checkpointed to
school_id_802_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 802
SCHOOL_NAME = 'University of Mount Olive'
CAREERS_LINK = 'https://umo.edu/employment/'
ATS_PLATFORM = 'own website'
USE_LLM = False

_ROWS = None

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """one opening from the data service the employment page itself calls (title,
    department, type, description)."""
    import json, urllib.request
    global _ROWS
    if _ROWS is None:
        def get(u, h=None):
            return urllib.request.urlopen(urllib.request.Request(u, headers=dict({'User-Agent': 'Mozilla/5.0'}, **(h or {}))), timeout=40).read().decode('utf-8', 'replace')
        html = get(CAREERS_LINK)
        base = re.search(r"SUPABASE_URL\s*=\s*'([^']+)'", html).group(1); key = re.search(r"SUPABASE_ANON_KEY\s*=\s*'([^']+)'", html).group(1)
        _ROWS = {r['slug']: r for r in json.loads(get(base + '/rest/v1/jobs?select=*&active=eq.true', {'apikey': key, 'Authorization': 'Bearer ' + key}))}
    r = _ROWS.get(url.partition('#')[2])
    if not r:
        raise RuntimeError('opening no longer listed')
    from bs4 import BeautifulSoup
    body = BeautifulSoup(r.get('description') or '', 'html.parser').get_text(' ', strip=True)
    return r['title'][:250], re.sub(r'\s+', ' ', f"{r['title']}. Department: {r.get('department') or ''}. {r.get('type') or ''}. Posted {r.get('posted_date') or ''}. {body}")[:20000]


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
