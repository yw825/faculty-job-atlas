"""
Job postings scraper for school_id 904 - University of Nevada-Reno (US)
ATS platform: Workday (detected: workday)
Careers link: https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=dddb2e55fbdf018c7a8b5718563592a1&locations=dddb2e55fbdf014cadc74f18563588a1&locations=dddb2e55fbdf01a639587d185635c4a1&locations=dddb2e55fbdf01c792a08f185635dda1&locations=dddb2e55fbdf013f6327481856357ea1&locations=dddb2e55fbdf010fb9a479185635bfa1&locations=dddb2e55fbdf014d1b1788185635d3a1&locations=dddb2e55fbdf01d2538e6e185635b0a1&locations=dddb2e55fbdf010679085f1856359ca1&locations=dddb2e55fbdf01e12d6e4418563579a1&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313

University of Nevada-Reno runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_904_job_posts.csv (school_id, post_link).
Checkpointed to school_id_904_job_postings.checkpoint next to this script.

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

SCHOOL_ID = 904
SCHOOL_NAME = 'University of Nevada-Reno'
CAREERS_LINK = 'https://nshe.wd1.myworkdayjobs.com/UNR-external?locations=dddb2e55fbdf018c7a8b5718563592a1&locations=dddb2e55fbdf014cadc74f18563588a1&locations=dddb2e55fbdf01a639587d185635c4a1&locations=dddb2e55fbdf01c792a08f185635dda1&locations=dddb2e55fbdf013f6327481856357ea1&locations=dddb2e55fbdf010fb9a479185635bfa1&locations=dddb2e55fbdf014d1b1788185635d3a1&locations=dddb2e55fbdf01d2538e6e185635b0a1&locations=dddb2e55fbdf010679085f1856359ca1&locations=dddb2e55fbdf01e12d6e4418563579a1&jobFamilyGroup=dddb2e55fbdf019e6a5085a6fb347313&jobFamilyGroup=dddb2e55fbdf0197f85f98a6fb347f13&jobFamilyGroup=dddb2e55fbdf01b2d73d9ea6fb348313'
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
