"""
Job postings scraper for school_id 1592 - Thompson Rivers University (Canada)
ATS platform: HRSmart
Careers link: https://tru.hua.hrsmart.com/hr/ats/JobSearch/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Thompson Rivers University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is /hr/ats/Posting/view/<id> on the HRSmart board.

Writes school_job_posts/school_id_1592_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1592_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1592
SCHOOL_NAME = 'Thompson Rivers University'
CAREERS_LINK = 'https://tru.hua.hrsmart.com/hr/ats/JobSearch/search'
ATS_PLATFORM = 'HRSmart'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# A real HRSmart posting is /hr/ats/Posting/view/<id>. The generic
# job-shaped filter also matched the site's own search machinery -- the
# quick/advanced search forms, "view all", "create account", the pagination
# links, and 25 "find similar jobs" lens.php links -- which then appeared as
# 42 postings with a blank title (confirmed live).
POSTING_RE = re.compile(r'/hr/ats/Posting/view/\d+')


PAGE_URL = ('https://tru.hua.hrsmart.com/hr/ats/JobSearch/search/'
            'jobSearchPaginationExternal_page:{page}')


POSTING_RE = re.compile(r'^https://tru\.hua\.hrsmart\.com/hr/ats/Posting/view/\d+$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
