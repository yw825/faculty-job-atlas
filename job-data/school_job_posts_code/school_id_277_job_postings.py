"""
Job postings scraper for school_id 277 - Georgia State University
ATS platform: PeopleAdmin
Careers link: https://facultycareers.gsu.edu/postings/search

gsu.taleo.net answers with an SSO redirect stub (saml20authnrequestservlet),
not a job board, so this school sat at zero. Its faculty postings are on a
PeopleAdmin board, which serves 30 openings over plain HTTP.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 277
SCHOOL_NAME = 'Georgia State University'
CAREERS_LINK = 'https://facultycareers.gsu.edu/postings/search'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

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
