"""
Job postings scraper for school_id 1690 - Karlsruhe Institute of Technology (Germany)
ATS platform: own website
Careers link: https://www.kit.edu/career/jobs.php

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Karlsruhe Institute of Technology; nothing here affects any
other school's script.

TUNED FIND_LINKS
KIT's jobs page points to its job portal, jobs.pse.kit.edu, which lists
every opening as /(de|en)/jobs/<id>/<slug>. A job can be linked in both
languages, so links are deduplicated by id.

Writes school_job_posts/school_id_1690_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1690_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1690
SCHOOL_NAME = 'Karlsruhe Institute of Technology'
CAREERS_LINK = 'https://www.kit.edu/career/jobs.php'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


PORTAL = 'https://jobs.pse.kit.edu/de/jobs'
POSTING_RE = re.compile(r'^https://jobs\.pse\.kit\.edu/(?:de|en)/jobs/(\d+)/[^/?#]+$', re.I)


def find_links():
    status, html = lib.fetch_static(PORTAL, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(PORTAL, 4000)
    by_id = {}
    for url in lib.extract_links(html, PORTAL):
        m = POSTING_RE.match(url)
        if m:
            by_id.setdefault(m.group(1), url)   # a job is linked in de and en
    return list(by_id.values())


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
