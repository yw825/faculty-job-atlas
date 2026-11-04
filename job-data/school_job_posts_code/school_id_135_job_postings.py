"""
Job postings scraper for school_id 135 - University of San Diego (US)
ATS platform: own website
Careers link: https://jobs.sandiego.edu/jobs/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of San Diego; nothing here affects any
other school's script.

Link check (ok): 9 posting-shaped links found -- rendered.

TUNED FIND_LINKS
A posting is exactly one slug under /jobs/ on the board's own host
(/jobs/<title>-<city>-<state>-united-states). The listing paginates with
?page=N, so every page is walked until one adds nothing new
(lib.scrape_paged_board); /jobs/search pages are the pager itself.

Writes school_job_posts/school_id_135_job_posts.csv (school_id, post_link).
Checkpointed to school_id_135_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 135
SCHOOL_NAME = 'University of San Diego'
CAREERS_LINK = 'https://jobs.sandiego.edu/jobs/search'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://jobs\.sandiego\.edu/jobs/(?!search\b|job-alerts\b|job-categories\b)'
                        r'[a-z0-9][a-z0-9-]+$', re.I)


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
