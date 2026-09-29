"""
Job postings scraper for school_id 1906 - Audencia Business School (France)
ATS platform: Teamtailor
Careers link: https://audencia.teamtailor.com/jobs

There is no shared Teamtailor adapter in job_postings_lib (Audencia is the
first school in the set on that vendor), so find_links() below is THIS
SCHOOL'S OWN scraping logic, owned entirely by this file. If more Teamtailor
schools turn up later, this is the logic to promote into a real adapter.

Teamtailor serves the whole list in the static HTML, so no render is needed
-- rendering was tried and returns the same 11-12 links from a 143 KB page
rather than the 100 KB static one, so it buys nothing. Postings are linked
as /jobs/<numeric id>-<slug>; the numeric-id-plus-slug shape is what
separates real postings from the board's own nav links (/jobs, /jobs.rss).
There is no pagination on this board.

Worth knowing for later: at the time of writing this board carried zero
faculty postings -- all 12 are internships (`stage-...`) and administrative
roles. That is a point-in-time fact about Audencia's hiring, not a fault in
this scraper; academic posts will be collected the same way when listed.

Writes school_job_posts/school_id_1906_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1906_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1906
SCHOOL_NAME = 'Audencia Business School'
CAREERS_LINK = 'https://audencia.teamtailor.com/jobs'
ATS_PLATFORM = 'Teamtailor'

POSTING = re.compile(r'https://audencia\.teamtailor\.com/jobs/\d+-[a-z0-9\-]+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=20)
    if status != 200 or not html:
        raise RuntimeError(f'audencia teamtailor board returned http={status}')
    links = sorted(set(POSTING.findall(html)))
    if not links:
        raise RuntimeError('audencia teamtailor board listed no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
