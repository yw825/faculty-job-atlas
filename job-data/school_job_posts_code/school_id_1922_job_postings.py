"""
Job postings scraper for school_id 1922 - Louisiana State University-Eunice (US)
ATS platform: Workday (detected: workday)
Careers link: https://lsu.wd1.myworkdayjobs.com/LSU?hiringCompany=7a9995fc77aa101f333e8777d04228d3&workerSubType=7a9995fc77aa101fcf3b27f556ddb30b

Louisiana State University-Eunice runs on a shared ATS platform -- every
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

Writes school_job_posts/school_id_1922_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1922_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
LSU's Workday board serves several campuses; the link carries the board's
own Campus Location and Job Type (Faculty) filters for LSU Eunice.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1922
SCHOOL_NAME = 'Louisiana State University-Eunice'
CAREERS_LINK = 'https://lsu.wd1.myworkdayjobs.com/LSU?hiringCompany=7a9995fc77aa101f333e8777d04228d3&workerSubType=7a9995fc77aa101fcf3b27f556ddb30b'
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
