"""
Job postings scraper for school_id 471 - Bethel College-North Newton (US)
ATS platform: own website
Careers link: https://jobs.bethelks.edu/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

The careers link was already the right host, but the generic word filter
collected the site's own navigation alongside the openings, and pulled in a
"Title IX Coordinator" policy page from www.bethelks.edu -- a different host
entirely -- because the phrase names a role.

Bethel's real openings all sit under one path on the jobs host
(.../career-opportunities/current-position-openings/<slug>), so that is what
this matches: "BCAPA Music Instructor", "Major Gift Officer", "Assistant
Coach: Track and Field - throws". It is a short list because the college is
small, not because the scrape is truncated.

Note that path is only where the postings LIVE -- it is not itself a page.
Requesting it returns 404; the listing that links to them is the site root,
which is why that is the careers link here.

Writes school_job_posts/school_id_471_job_posts.csv (school_id, post_link).
Checkpointed to school_id_471_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
jobs.bethelks.edu forwards to the current-position-openings page; each
opening is a page under it (the audit found no faculty opening).
"""
import os
import re
import sys
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 471
SCHOOL_NAME = 'Bethel College-North Newton'
CAREERS_LINK = 'https://jobs.bethelks.edu/'
ATS_PLATFORM = 'own website'

HOST = 'jobs.bethelks.edu'
POSTING_PATH = re.compile(
    r'^/about/who-we-are/career-opportunities/current-position-openings/'
    r'[a-z0-9][a-z0-9\-]{3,120}/?$', re.I)

LIST = 'https://forms.bethelks.edu/about/who-we-are/career-opportunities/current-position-openings'
POSTING_RE = re.compile(r'^https://forms\.bethelks\.edu/about/who-we-are/career-opportunities/current-position-openings/[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(LIST, POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
