"""
Job info scraper for school_id 247 - Florida International University (US)
ATS platform: own website
Careers link: https://search.careers.fiu.edu/?role=employee&sort=newest

Reads posting URLs from school_id_247_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_247_job_info.csv. Checkpointed to
school_id_247_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 247
SCHOOL_NAME = 'Florida International University'
CAREERS_LINK = 'https://search.careers.fiu.edu/?role=employee&sort=newest'
ATS_PLATFORM = 'own website'
USE_LLM = False

_JOBS = {}

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """The posting's record in search.careers.fiu.edu/api/jobs (fetched once
    per run): title, business unit, department, job family, description."""
    import json
    import re
    from bs4 import BeautifulSoup
    if not _JOBS:
        status, text = jinfo.jlib.fetch_static('https://search.careers.fiu.edu/api/jobs', timeout=60)
        if status != 200:
            raise RuntimeError(f'FIU jobs service status={status}')
        for j in json.loads(text)['JOB_POSTINGS']:
            _JOBS[str(j.get('JOB_OPENING_ID'))] = j
    m = re.search(r'JobOpeningId=(\d+)', url)
    job = _JOBS.get(m.group(1)) if m else None
    if job is None:
        raise RuntimeError('posting no longer listed')
    lead = []
    if job.get('OPEN_DT'):
        lead.append(f"Posted Date: {job['OPEN_DT'][:10]}")
    if job.get('DEPARTMENT'):
        lead.append(f"Department: {job['DEPARTMENT']}")
    for key, label in (('BUSINESS_UNIT', 'College'), ('JOB_FAMILY', 'Job family'), ('LOCATION', 'Location')):
        if job.get(key):
            lead.append(f'{label}: {job[key]}')
    body = BeautifulSoup(job.get('DESCRIPTION') or '', 'html.parser').get_text(' ', strip=True)
    return (job.get('POSTING_TITLE') or '').strip()[:250], re.sub(r'\s+', ' ', ' '.join(lead) + ' ' + body)[:20000]


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
