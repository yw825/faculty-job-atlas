"""
Job postings scraper for school_id 1776 - University of Oxford (United Kingdom)
ATS platform: CoreHR (detected: corehr)
Careers link: https://my.corehr.com/pls/uoxrecruit/erq_search_package.search_form?p_company=10&p_internal_external=E

The original careers_link had no query params, which returned nothing
useful -- this one filters to academic external postings and matches the
"21 open academic postings" confirmed live on the real site. CoreHR is a
real shared platform (10 schools in this dataset run on it), so this uses
the shared job_postings_lib.scrape_corehr adapter -- built directly from
investigating this school -- rather than one-off logic here.

Writes school_job_posts/school_id_1776_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1776_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
CoreHR board: the search form is POSTed and its "Next" form followed in one
session (lib.corehr_search), as for the Irish universities; the old adapter
built display_form URLs, which answer 403. Postings are the public
erq_jobspec_version_4.jobspec?p_id=<id> stubs.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1776
SCHOOL_NAME = 'University of Oxford'
CAREERS_LINK = 'https://my.corehr.com/pls/uoxrecruit/erq_search_package.search_form?p_company=10&p_internal_external=E'
ATS_PLATFORM = 'CoreHR'
PLATFORM = 'corehr'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [url for url, _title in lib.corehr_search(CAREERS_LINK)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
