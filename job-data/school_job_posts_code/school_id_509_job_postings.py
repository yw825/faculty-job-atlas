"""
Job postings scraper for school_id 509 - Louisiana State University-Alexandria (US)
ATS platform: Workday (detected: workday)
Careers link: https://lsu.wd1.myworkdayjobs.com/LSU?hiringCompany=7a9995fc77aa101f333e7b1c1f7228b5

Louisiana State University-Alexandria runs on a shared ATS platform -- every
school on workday uses the same underlying site software, so this calls the
shared job_postings_lib.scrape_workday adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every workday school, define find_links() below and
pass it to run_checkpointed instead of editing the shared adapter.

The LSU board is shared across the whole system: unfiltered it returns 280
postings belonging to five employers (A&M 182, Eunice 36, the Agricultural
Center 33, Alexandria 22, Pennington Biomedical 7). Both LSU schools here
were pointed at it unfiltered and so held an identical 359 links each --
every A&M posting also appeared under Alexandria.

The dimension that separates them is the "hiringCompany" facet, not a
location one. scrape_workday forwards any query parameter it does not
recognise as navigation into the API's appliedFacets, so pinning the id in
the careers link is all that is needed: Alexandria returns 22 of the 280.

Writes school_job_posts/school_id_509_job_posts.csv (school_id, post_link).
Checkpointed to school_id_509_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 509
SCHOOL_NAME = 'Louisiana State University-Alexandria'
CAREERS_LINK = ('https://lsu.wd1.myworkdayjobs.com/LSU'
                '?hiringCompany=7a9995fc77aa101f333e7b1c1f7228b5')
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
