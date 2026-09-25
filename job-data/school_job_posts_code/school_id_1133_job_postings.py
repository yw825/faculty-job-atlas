"""
Job postings scraper for school_id 1133 - University of Pittsburgh-Bradford
ATS platform: Taleo
Careers link: https://cfopitt.taleo.net/careersection/pitt_staff_external/jobsearch.ftl

The careers link pointed at ONE job (jobdetail.ftl?job=26003465) rather than
a listing. This career section renders 25 job links directly in its HTML.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1133
SCHOOL_NAME = 'University of Pittsburgh-Bradford'
CAREERS_LINK = 'https://cfopitt.taleo.net/careersection/pitt_staff_external/jobsearch.ftl'
ATS_PLATFORM = 'Taleo'
PLATFORM = 'taleo'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
