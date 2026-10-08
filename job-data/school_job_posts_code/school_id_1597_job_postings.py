"""
Job postings scraper for school_id 1597 - Royal Roads University (Canada)
ATS platform: HRdepartment/MUA
Careers link: https://royalroads.mua.hrdepartment.com/hr/ats/JobSearch/viewAll

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Royal Roads University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is /hr/ats/Posting/view/<id>. The board's own page-size
control (pageSize:100) is used so one page holds every opening.

Writes school_job_posts/school_id_1597_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1597_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1597
SCHOOL_NAME = 'Royal Roads University'
CAREERS_LINK = 'https://royalroads.mua.hrdepartment.com/hr/ats/JobSearch/viewAll'
ATS_PLATFORM = 'HRdepartment/MUA'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://royalroads\.mua\.hrdepartment\.com/hr/ats/Posting/view/\d+$', re.I)
ALL_ON_ONE_PAGE = ('https://royalroads.mua.hrdepartment.com/hr/ats/JobSearch/viewAll/'
                   'jobSearchPaginationExternal_pageSize:100/jobSearchPaginationExternal_page:1')


def find_links():
    return lib.scrape_matching(ALL_ON_ONE_PAGE, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
