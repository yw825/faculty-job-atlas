"""
Job postings scraper for school_id 169 - University of Denver (US)
ATS platform: own website
Careers link: https://jobs.du.edu/en-us/filter/?search=&search-keyword=&work-type=adjunct%20faculty&work-type=faculty%20full-time&job-mail-subscribe-privacy=agree

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Denver; nothing here affects any
other school's script.

Link check (ok): 25 posting-shaped links found -- rendered.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_169_job_posts.csv (school_id, post_link).
Checkpointed to school_id_169_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Classic PageUp board: lib.scrape_pageup_listing asks for the whole (filtered)
list (page-items=500, paging beyond that) and keeps .../job/<id>/<slug>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 169
SCHOOL_NAME = 'University of Denver'
CAREERS_LINK = 'https://jobs.du.edu/jobs/search'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


_JOB_HREF_RE = re.compile(r'href="(?:https://jobs\.du\.edu)?(/jobs/(?!search)[a-z0-9][^"?#]*)"')


def find_links():
    """Denver left PageUp for a new board in October 2026 (the old filter
    link now 404s, "Looking for open faculty positions? View our open
    roles."). The new one sits behind an AWS WAF check, so pages are
    rendered; it pages with ?page=N (25 a page) and has no faculty filter,
    so every job is read and the map's faculty filter does the rest."""
    links = []
    for page in range(1, 30):
        html = lib.fetch_rendered(f'{CAREERS_LINK}?page={page}', wait_ms=3000)
        if lib.is_fetch_failure(html) or not html:
            if page == 1:
                raise RuntimeError(f'denver board not reachable: {html[:80]}')
            break
        new = [f'https://jobs.du.edu{h}' for h in _JOB_HREF_RE.findall(html)]
        new = [u for u in dict.fromkeys(new) if u not in links]
        if not new:   # past the last page the board repeats the first
            break
        links += new
    if not links:
        raise RuntimeError('denver board listed no jobs')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
