"""
Job postings scraper for school_id 1202 - University of Pittsburgh-Pittsburgh Campus
ATS platform: Taleo
Careers link: https://cfopitt.taleo.net/careersection/pitt_faculty_external/jobsearch.ftl

pitt_internal is an SSO-gated section that answers with a redirect stub.
pitt_faculty_external is the public faculty board: 25 job links in HTML.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1202
SCHOOL_NAME = 'University of Pittsburgh-Pittsburgh Campus'
CAREERS_LINK = 'https://cfopitt.taleo.net/careersection/pitt_faculty_external/jobsearch.ftl'
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
