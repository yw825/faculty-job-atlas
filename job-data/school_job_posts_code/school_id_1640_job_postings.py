"""
Job postings scraper for school_id 1640 - Concordia University (Canada)
ATS platform: own website
Careers link: https://www.concordia.ca/hr/jobs/openings.html#academic

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Concordia University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps: the openings page links each faculty's jobs page
(/<faculty>/about/jobs.html, plus the library's), and those link each ad.
Hubs link the CMS path /content/shared/en/jobs/<unit>/<slug>.html, stored
as its public form /jobs/<unit>/<slug>.html. Invigilator postings (under
/<faculty>/about/jobs/invigila...) are not academic posts and do not match.

Writes school_job_posts/school_id_1640_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1640_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1640
SCHOOL_NAME = 'Concordia University'
CAREERS_LINK = 'https://www.concordia.ca/hr/jobs/openings.html#academic'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


HUB_RE = re.compile(r'^https://(?:www\.concordia\.ca/[^/?#]+/about/jobs\.html|library\.concordia\.ca/about/jobs/)$', re.I)
POSTING_RE = re.compile(r'^https://www\.concordia\.ca/(?:content/shared/en/)?jobs/[^/?#]+/[^/?#]+\.html$', re.I)


def public_url(url):
    # hubs link the CMS path; the public page is /jobs/<unit>/<slug>.html
    return url.replace('/content/shared/en/jobs/', '/jobs/')


def find_links():
    return lib.scrape_two_hop(CAREERS_LINK, HUB_RE, POSTING_RE, normalize=public_url)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
