"""
Job postings scraper for school_id 1924 - Louisiana State University-Health Sciences Center New Orleans (US)
ATS platform: Workday (detected: workday)
Careers link: https://careers.lsuhsc.edu/jobs/search?page=1&employment_type_uids%5B%5D=9290c84c437e451fd084a786a6367d37&query=

Louisiana State University-Health Sciences Center New Orleans runs on a shared ATS platform -- every
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

Writes school_job_posts/school_id_1924_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1924_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
LSU Health New Orleans has its own board (careers.lsuhsc.edu), filtered here
to its Faculty employment type and paged by ?page=N.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1924
SCHOOL_NAME = 'Louisiana State University-Health Sciences Center New Orleans'
CAREERS_LINK = 'https://careers.lsuhsc.edu/jobs/search?page=1&employment_type_uids%5B%5D=9290c84c437e451fd084a786a6367d37&query='
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://careers\.lsuhsc\.edu/jobs/(?!search\b|job-alerts\b|job-categories\b)[a-z0-9][a-z0-9-]+$', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
