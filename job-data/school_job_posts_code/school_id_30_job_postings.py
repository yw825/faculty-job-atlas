"""
Job postings scraper for school_id 30 - The University of Alabama (US)
ATS platform: own website
Careers link: https://careers.ua.edu/jobs/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

This school was pointed at https://careers.ua.edu/faculty, which is a
landing page: rendered, it yields category links (/jobs/search/AS,
/jobs/search/ENG ...) and not one posting. Every opening was missed,
including the Mechanical Engineering Assistant Professor (530028) a user
found by hand on 2026-09-16.

The real board is /jobs/search, which is JS-rendered and PAGINATED at 30
postings per page (?page=N), alphabetical by title -- 530028 sits on page
5. Nothing on page 1 hints that more pages exist, which is why the original
"fetch one page" shape could never have found it. Note the category URLs
(/jobs/search/ENG) serve the same unfiltered list, so there is no shortcut
to the faculty subset; we page through everything and let the later stages
classify.

Writes school_job_posts/school_id_30_job_posts.csv (school_id, post_link).
Checkpointed to school_id_30_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 30
SCHOOL_NAME = 'The University of Alabama'
CAREERS_LINK = 'https://careers.ua.edu/jobs/search'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

# A posting URL is /jobs/<title-slug>-<requisition id>-<location>. The
# listing's own furniture (/jobs/search, /jobs/search/ENG, /jobs/job-alerts,
# /jobs/job-categories) must not match, hence the digits requirement: every
# real posting carries a 5-6 digit requisition number.
POSTING_RE = re.compile(r'https?://careers\.ua\.edu/jobs/[a-z0-9][a-z0-9-]*?-\d{5,6}-[a-z0-9-]+', re.I)

MAX_PAGES = 25          # 5 pages as of 2026-09; headroom without running away
PAGE_WAIT_MS = 3000     # the list is rendered client-side


def find_links():
    seen = []
    known = set()
    for page in range(1, MAX_PAGES + 1):
        url = f'{CAREERS_LINK}?page={page}'
        html = lib.fetch_rendered(url, wait_ms=PAGE_WAIT_MS)
        if lib.is_fetch_failure(html):
            if page == 1:
                raise RuntimeError(html)
            break                     # keep what earlier pages gave us
        found = POSTING_RE.findall(html)
        fresh = [u for u in found if u not in known]
        if not fresh:
            break                     # past the last page: no new postings
        for u in fresh:
            known.add(u)
            seen.append(u)
    if not seen:
        raise RuntimeError('no postings found on any page of ' + CAREERS_LINK)
    return seen


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
