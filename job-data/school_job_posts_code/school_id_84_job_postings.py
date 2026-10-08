"""
Job postings scraper for school_id 84 - Vanguard University of Southern California (US)
ATS platform: own website
Careers link: https://www.vanguard.edu/resources/human-resources/vu-careers?post_category_id=165

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Vanguard University of Southern California; nothing here affects any
other school's script.

Link check (ok): 14 posting-shaped links found.

TUNED FIND_LINKS
Each opening links to its Paychex AppOne requisition,
MainInfoReq.asp?R_ID=<id>. The page's own vanguard.edu links are filters
and navigation.

Writes school_job_posts/school_id_84_job_posts.csv (school_id, post_link).
Checkpointed to school_id_84_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 84
SCHOOL_NAME = 'Vanguard University of Southern California'
CAREERS_LINK = 'https://www.vanguard.edu/resources/human-resources/vu-careers?post_category_id=165'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://recruiting\.myapps\.paychex\.com/appone/MainInfoReq\.asp\?R_ID=\d+$', re.I)


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
