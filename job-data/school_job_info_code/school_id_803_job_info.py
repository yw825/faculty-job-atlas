"""
Job info scraper for school_id 803 - Chowan University (US)
ATS platform: own website
Careers link: https://www.chowan.edu/about/offices/human-resources/

Reads posting URLs from school_id_803_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_803_job_info.csv. Checkpointed to
school_id_803_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 803
SCHOOL_NAME = 'Chowan University'
CAREERS_LINK = 'https://www.chowan.edu/about/offices/human-resources/'
ATS_PLATFORM = 'own website'
USE_LLM = False

_ADVERTS = None

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """the opening's Paycor advert (the stored address is the school page with
    ?gni=<id>); the advert address is taken from the page's Paycor frame."""
    global _ADVERTS
    if _ADVERTS is None:
        _ADVERTS = {u.rsplit('id=', 1)[1].split('&')[0]: u for u in jinfo.jlib.scrape_paycor_frame(CAREERS_LINK)}
    gni = re.search(r'gni=([0-9a-zA-Z]+)', url).group(1)
    if gni not in _ADVERTS:
        raise RuntimeError('opening no longer listed')
    return jinfo.fetch_detail_paycor(_ADVERTS[gni])


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
