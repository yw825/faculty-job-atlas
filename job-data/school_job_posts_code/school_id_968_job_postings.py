"""
Job postings scraper for school_id 968 - Marymount Manhattan College (US)
ATS platform: own website
Careers link: https://service.northeastern.edu/hr?id=kb_article_view&sysparm_article=KB000024399&sys_kb_id=0216c71c47168f10c5a12675d36d43c8&spa=1

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Marymount Manhattan College; nothing here affects any
other school's script.

Link check (ok): 25 posting-shaped links found -- rendered.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_968_job_posts.csv (school_id, post_link).
Checkpointed to school_id_968_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 968
SCHOOL_NAME = 'Marymount Manhattan College'
CAREERS_LINK = 'https://service.northeastern.edu/hr?id=kb_article_view&sysparm_article=KB000024399&sys_kb_id=0216c71c47168f10c5a12675d36d43c8&spa=1'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK,
                             href_pattern=lib.COMMON_JOB_URL_HINTS,
                             text_pattern=lib.COMMON_JOB_URL_HINTS)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
