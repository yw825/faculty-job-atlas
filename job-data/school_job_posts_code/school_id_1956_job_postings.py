"""
Job postings scraper for school_id 1956 - Ohio State University-Newark (US)
ATS platform: Workday
Careers link: https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515&locations=819c1ab743bd015ff0249600650198b6

Ohio State's Workday board, Academic + Post Doctoral groups, Newark location.

Writes school_job_posts/school_id_1956_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1956_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1956
SCHOOL_NAME = "Ohio State University-Newark"
CAREERS_LINK = 'https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515&locations=819c1ab743bd015ff0249600650198b6'
ATS_PLATFORM = 'Workday'

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
