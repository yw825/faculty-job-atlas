"""
Job postings scraper for school_id 358 - The College of Idaho (US)
ATS platform: own website
Careers link: https://collegeofidaho.edu/careers

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for The College of Idaho; nothing here affects any
other school's script.

Link check (ok): 6 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_358_job_posts.csv (school_id, post_link).
Checkpointed to school_id_358_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The old link was a student career-sectors page. Openings are the PDF
adverts linked from /careers (the audit's example is one of them).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 358
SCHOOL_NAME = 'The College of Idaho'
CAREERS_LINK = 'https://collegeofidaho.edu/careers'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://collegeofidaho\.edu/wp-content/uploads/\d{4}/\d{2}/[^/]+\.pdf$', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
