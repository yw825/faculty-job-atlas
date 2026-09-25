"""
Job postings scraper for school_id 638 - Kettering University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.kettering.edu/

Kettering University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here.

The careers link was www.kettering.edu/co-op-career-design -- the page about
Kettering's co-op programme for STUDENTS looking for placements, not the
university's own hiring. It is job-shaped enough to pass a generic filter,
which is why the school recorded three links from it and no real postings.
Kettering's board is jobs.kettering.edu, whose Atom feed lists 12.

Writes school_job_posts/school_id_638_job_posts.csv (school_id, post_link).
Checkpointed to school_id_638_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 638
SCHOOL_NAME = 'Kettering University'
CAREERS_LINK = 'https://jobs.kettering.edu/'
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
