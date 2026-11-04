"""
Job postings scraper for school_id 1789 - University of New South Wales (Australia)
ATS platform: own website (a PageUp-backed careers site, but the listing
pages are plain server-rendered HTML -- no PageUp API needed)
Careers link: https://external-careers.jobs.unsw.edu.au/

CUSTOMIZED (confirmed live): this school was previously recording ZERO
postings, but nothing here is actually blocked -- the page loads fine and
the generic job-shaped link filter simply didn't match its URL scheme.
Postings are plain links of the form /en/job/<id>/<slug>. The default
listing shows 20 per page; ?page-items=100 returns them all in one request
(97 confirmed live), and the loop below still pages on in case that cap is
ever raised past 100.

Note UNSW's apply flow hands off to secure.dc2.pageuppeople.com, but the
posting pages themselves stay on this host, so the stable per-posting URL
is the one recorded here.

Writes school_job_posts/school_id_1789_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1789_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1789
SCHOOL_NAME = 'University of New South Wales'
CAREERS_LINK = 'https://external-careers.jobs.unsw.edu.au/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

LISTING = 'https://external-careers.jobs.unsw.edu.au/en/listing/?page={page}&page-items=100'
JOB_HREF_RE = re.compile(r'^/en/job/\d+/')


def find_links():
    links, seen = [], set()
    for page in range(1, 15):
        html = lib.fetch_rendered(LISTING.format(page=page), wait_ms=4000)
        if lib.is_fetch_failure(html):
            if page == 1:
                raise RuntimeError(html)
            break
        found = lib.extract_links(html, CAREERS_LINK, href_pattern=JOB_HREF_RE)
        new = [u for u in found if u not in seen]
        if not new:
            break
        seen.update(new)
        links.extend(new)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
