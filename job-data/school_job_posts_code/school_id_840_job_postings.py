"""
Job postings scraper for school_id 840 - Creighton University (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://www.creighton.edu/creighton-faculty-career

Creighton University runs on a shared ATS platform -- every school on oracle uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_840_job_posts.csv (school_id, post_link).
Checkpointed to school_id_840_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to Creighton's faculty careers page; each
opening is a page on creighton.edu linked from its list (the Oracle board is
staff).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 840
SCHOOL_NAME = 'Creighton University'
CAREERS_LINK = 'https://www.creighton.edu/creighton-faculty-career'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

POSTING_RE = re.compile(r'^https://www\.creighton\.edu/(?!creighton-faculty-career)[a-z0-9-]*(?:professor|faculty|lecturer|chair|instructor|dean|director|fellow)[a-z0-9-]*$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE, first_page=0)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
