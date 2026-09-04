"""
Job postings scraper for school_id 46 - University of Arkansas at Little Rock (US)
ATS platform: Workday (detected: workday)
Careers link: https://uasys.wd5.myworkdayjobs.com/UASYS?hiringCompany=720b21cbdf2401e26b5b1759c4019006&locations=17a66cdad982014d322b8c49ca003c4a&timeType=8676082fcc89011e20fa6c2e71495700

University of Arkansas at Little Rock runs on a shared ATS platform -- every school on workday uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_46_job_posts.csv (school_id, post_link).
Checkpointed to school_id_46_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 46
SCHOOL_NAME = 'University of Arkansas at Little Rock'
CAREERS_LINK = 'https://uasys.wd5.myworkdayjobs.com/UASYS?hiringCompany=720b21cbdf2401e26b5b1759c4019006&locations=17a66cdad982014d322b8c49ca003c4a&timeType=8676082fcc89011e20fa6c2e71495700'
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
