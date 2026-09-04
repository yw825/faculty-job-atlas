"""
Job postings scraper for school_id 178 - Colorado State University Pueblo (US)
ATS platform: Workday (detected: workday)
Careers link: https://csusystem.wd12.myworkdayjobs.com/en-US/pueblo_careers?locations=c42207b011c11000e4a22ee1cf1e0000&jobFamilyGroup=c42207b011c11000d2dd549d70320000

Colorado State University Pueblo runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_178_job_posts.csv (school_id, post_link).
Checkpointed to school_id_178_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 178
SCHOOL_NAME = 'Colorado State University Pueblo'
CAREERS_LINK = 'https://csusystem.wd12.myworkdayjobs.com/en-US/pueblo_careers?locations=c42207b011c11000e4a22ee1cf1e0000&jobFamilyGroup=c42207b011c11000d2dd549d70320000'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

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
