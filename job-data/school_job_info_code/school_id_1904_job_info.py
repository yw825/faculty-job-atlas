"""
Job info scraper for school_id 1904 - NEOMA Business School (France)
ATS platform: own website
Careers link: https://neoma-bs.com/offres_emploi

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if NEOMA Business School's posting
pages need something the default doesn't handle; nothing here affects any
other school's script.

NEOMA's postings are public apply.interfolio.com pages harvested off its
own vacancies page, exactly like Rice (school_id 1394). They are read one
by one with the generic detail fetcher rather than through the interfolio
BULK adapter, because that adapter needs a school-owned Interfolio board to
enumerate and NEOMA has none -- it only links out to Interfolio.

Reads posting URLs from school_id_1904_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_1904_job_info.csv. Checkpointed to
school_id_1904_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1904
SCHOOL_NAME = 'NEOMA Business School'
CAREERS_LINK = 'https://neoma-bs.com/offres_emploi'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    return jinfo.fetch_detail_generic(url)


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
