"""
Job postings scraper for school_id 567 - Anna Maria College (US)
ATS platform: own website
Careers link: https://annamaria.edu/work-at-anna-maria/faculty-staff-jobs/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Anna Maria College; nothing here affects any
other school's script.

Link check (review): 1 posting-shaped links found -- rendered few job-shaped links.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_567_job_posts.csv (school_id, post_link).
Checkpointed to school_id_567_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to the faculty & staff jobs page (read
statically -- the site does not finish loading in a browser). Openings would
be pages or PDFs linked under it; the audit found none.

"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 567
SCHOOL_NAME = 'Anna Maria College'
CAREERS_LINK = 'https://annamaria.edu/work-at-anna-maria/faculty-staff-jobs/'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://annamaria\.edu/(?:work-at-anna-maria/faculty-staff-jobs/[a-z0-9-]+/$|wp-content/uploads/.+(?:job|position|faculty|professor|adjunct).*\.pdf$)', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = None, ''
    for _try in range(3):
        status, html = lib.fetch_static(CAREERS_LINK, timeout=90)
        if status == 200:
            break
    if status != 200:
        raise RuntimeError(f'jobs page status={status}')
    return [u for u in lib.extract_links(html, CAREERS_LINK) if POSTING_RE.search(u)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
