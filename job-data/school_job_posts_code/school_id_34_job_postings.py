"""
Job postings scraper for school_id 34 - Lyon College (US)
ATS platform: own website
Careers link: https://lyon.isolvedhire.com/jobs/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Lyon College; nothing here affects any
other school's script.

Link check (ok): 8 posting-shaped links found.

TUNED FIND_LINKS
The board is iSolved Hire; each posting is lyon.isolvedhire.com/jobs/<id>.
The list is built client-side, so the page is rendered.

Writes school_job_posts/school_id_34_job_posts.csv (school_id, post_link).
Checkpointed to school_id_34_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 34
SCHOOL_NAME = 'Lyon College'
CAREERS_LINK = 'https://lyon.isolvedhire.com/jobs/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://lyon\.isolvedhire\.com/jobs/\d+$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
