"""
Job postings scraper for school_id 1043 - Ohio State University-Columbus (US)
ATS platform: Workday (detected: workday)
Careers link: https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515&locations=819c1ab743bd01f14b629c006501acb6&locations=e18a59cd58401001b106582a23ba0000&locations=819c1ab743bd0130a44a99006501a2b6

Ohio State University-Main Campus runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1043_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1043_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Workday board; the link carries the board's own filters (site, job category,
location).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1043
SCHOOL_NAME = "Ohio State University-Columbus"
CAREERS_LINK = 'https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515&locations=819c1ab743bd01f14b629c006501acb6&locations=e18a59cd58401001b106582a23ba0000&locations=819c1ab743bd0130a44a99006501a2b6'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.PLATFORM_ADAPTERS['workday'](CAREERS_LINK, SCHOOL_NAME)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
