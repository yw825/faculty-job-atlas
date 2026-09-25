"""
Job postings scraper for school_id 1535 - University of Wisconsin-Eau Claire (US)
ATS platform: Workday (detected: workday)
Careers link: https://wisconsin.wd1.myworkdayjobs.com/UW_Comprehensives?Institution=5adf054562b610142325d0db92c00000

University of Wisconsin-Eau Claire runs on a shared ATS platform -- every
school on workday uses the same underlying site software, so this calls the
shared job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below and
pass it to run_checkpointed instead of editing the shared adapter.

UW_Comprehensives is the UW SYSTEM board: unfiltered it returns 361 postings
belonging to twelve institutions, and four of our schools were pointed at it
unfiltered, so each stored all 403 links it had collected. Every posting
appeared on the map under all four -- La Crosse's vacancies showed under
Parkside and so on.

The board exposes an "Institution" facet whose twelve values are the
campuses. scrape_workday already forwards any query parameter it does not
recognise as navigation into the API's appliedFacets, so pinning the
institution id in the careers link is all that is needed: Eau Claire returns
27 of the 361.

Writes school_job_posts/school_id_1535_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1535_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1535
SCHOOL_NAME = 'University of Wisconsin-Eau Claire'
CAREERS_LINK = ('https://wisconsin.wd1.myworkdayjobs.com/UW_Comprehensives'
                '?Institution=5adf054562b610142325d0db92c00000')
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
