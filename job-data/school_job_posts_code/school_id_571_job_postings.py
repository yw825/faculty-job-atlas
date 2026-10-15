"""
Job postings scraper for school_id 571 - American International College (US)
ATS platform: ADP (detected: adp)
Careers link: https://www.higheredjobs.com/institution/search.cfm?University=American%20International%20College

American International College runs on a shared ATS platform -- every school on adp uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every adp school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_571_job_posts.csv (school_id, post_link).
Checkpointed to school_id_571_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to the college's HigherEdJobs list.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 571
SCHOOL_NAME = 'American International College'
CAREERS_LINK = 'https://www.higheredjobs.com/institution/search.cfm?University=American%20International%20College'
ATS_PLATFORM = 'ADP'
PLATFORM = 'adp'

POSTING_RE = re.compile(r'^https://www\.higheredjobs\.com/institution/details\.cfm\?JobCode=\d+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True, wait_ms=5000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
