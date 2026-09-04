"""
Job postings scraper for school_id 1106 - Oregon State University-Cascades Campus (US)
ATS platform: Workday (detected: workday)
Careers link: https://oregonstate.wd501.myworkdayjobs.com/OSU_Careers_Site

Oregon State University-Cascades Campus runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 2 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Oregon State University.

Writes school_job_posts/school_id_1106_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1106_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1106
SCHOOL_NAME = 'Oregon State University-Cascades Campus'
CAREERS_LINK = 'https://oregonstate.wd501.myworkdayjobs.com/OSU_Careers_Site'
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
