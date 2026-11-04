"""
Job postings scraper for school_id 1909 - Maynooth University (Ireland)
ATS platform: CoreHR
Careers link: https://my.corehr.com/pls/nuimrecruit/erq_search_package.search_form?p_company=1&p_internal_external=E

HOW THIS BOARD IS READ
The board is CoreHR. Opening its start_search_with_params URL directly shows
no jobs: a visitor has to open the search page and press "Search", which
POSTs the callErecruitDoSearch form, then press "Next" for each further page
of results. lib.corehr_search does exactly that in one session and stores
each job as CoreHR's own share link, .../erq_jobspec_version_4.jobspec?p_id=<id>,
which opens that job directly. It refuses a result short of the board's own
"Your search returned N results" count.

Writes school_job_posts/school_id_1909_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1909_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1909
SCHOOL_NAME = 'Maynooth University'
CAREERS_LINK = 'https://my.corehr.com/pls/nuimrecruit/erq_search_package.search_form?p_company=1&p_internal_external=E'
ATS_PLATFORM = 'CoreHR'
COMPETITION_TYPE = None

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [url for url, _title in lib.corehr_search(CAREERS_LINK, COMPETITION_TYPE)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
