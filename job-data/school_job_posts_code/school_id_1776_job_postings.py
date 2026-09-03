"""
Job postings scraper for school_id 1776 - University of Oxford (United Kingdom)
ATS platform: CoreHR (detected: corehr)
Careers link: https://my.corehr.com/pls/uoxrecruit/erq_search_version_4.start_search_with_params?p_company=10&p_internal_external=E&p_display_in_irish=N&p_competition_type=AC&p_force_type=E

The original careers_link had no query params, which returned nothing
useful -- this one filters to academic external postings and matches the
"21 open academic postings" confirmed live on the real site. CoreHR is a
real shared platform (10 schools in this dataset run on it), so this uses
the shared job_postings_lib.scrape_corehr adapter -- built directly from
investigating this school -- rather than one-off logic here.

Writes school_job_posts/school_id_1776_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1776_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1776
SCHOOL_NAME = 'University of Oxford'
CAREERS_LINK = 'https://my.corehr.com/pls/uoxrecruit/erq_search_version_4.start_search_with_params?p_company=10&p_internal_external=E&p_display_in_irish=N&p_competition_type=AC&p_force_type=E'
ATS_PLATFORM = 'CoreHR'
PLATFORM = 'corehr'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK, CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
