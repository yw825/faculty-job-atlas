"""
Job postings scraper for school_id 925 - D'Youville  University (US)
ATS platform: own website
Careers link: https://dyouville-university.prismhr-hire.com/job/726161/college-of-osteopathic-medicine-chair-primary-care

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for D'Youville  University; nothing here affects any
other school's script.

Link check (ok): 3 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_925_job_posts.csv (school_id, post_link).
Checkpointed to school_id_925_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 925
SCHOOL_NAME = 'D\'Youville  University'
CAREERS_LINK = 'https://dyouville-university.prismhr-hire.com/job/726161/college-of-osteopathic-medicine-chair-primary-care'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    """CUSTOMIZED: this school writes each opening as a SECTION of its
    careers page -- there is no per-job link to collect, which is why every
    link-based scraper returned 0 row(s) against 1 real openings
    on the page.

    Each section becomes CAREERS_LINK + '#' + a slug of its own heading,
    and school_id_925_job_info.py resolves that fragment back to the
    section's text."""
    return lib.scrape_inline_listing(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
