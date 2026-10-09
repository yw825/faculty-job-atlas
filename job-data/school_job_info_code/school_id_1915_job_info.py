"""
Job info scraper for school_id 1915 - South East Technological University (Ireland)
ATS platform: CoreHR
Careers link: https://my.corehr.com/pls/esbsheseturecruit/erq_search_package.search_form?p_company=1&p_internal_external=E

Each posting (.../erq_jobspec_version_4.jobspec?p_id=<id>) is a stub page that
auto-submits a form to the job's details; jinfo.fetch_detail_corehr submits it
and reads the vacancy-details cells. Where a job page has no title of its own,
the title is taken from the search-results row (same search the postings
script runs, cached for the run).

Writes school_job_info/school_id_1915_job_info.csv. Checkpointed to
school_id_1915_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1915
SCHOOL_NAME = 'South East Technological University'
CAREERS_LINK = 'https://my.corehr.com/pls/esbsheseturecruit/erq_search_package.search_form?p_company=1&p_internal_external=E'
ATS_PLATFORM = 'CoreHR'
COMPETITION_TYPE = None
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def fetch_detail(url):
    title, description = jinfo.fetch_detail_corehr(url)
    if not title:
        title = dict(jinfo.jlib.corehr_search(CAREERS_LINK, COMPETITION_TYPE)).get(url, '')
    return title, description


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
