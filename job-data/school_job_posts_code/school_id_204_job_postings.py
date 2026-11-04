"""
Job postings scraper for school_id 204 - George Washington University
ATS platform: PeopleAdmin
Careers link: https://www.gwu.jobs/postings/search

careers.gwu.edu is a landing page: it yielded two links, 'Our opportunities'
and an FAQ. The real board is gwu.jobs, a PeopleAdmin instance serving 92
postings. detect_platform reads gwu.jobs as 'dejobs', whose adapter returns
nothing here, so the platform is pinned explicitly.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 204
SCHOOL_NAME = 'George Washington University'
CAREERS_LINK = 'https://www.gwu.jobs/postings/search'
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
