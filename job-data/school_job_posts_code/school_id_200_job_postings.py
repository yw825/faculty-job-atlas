"""
Job postings scraper for school_id 200 - University of New Haven (US)
ATS platform: own website
Careers link: https://www.newhaven.edu:443/about/employment/job-opportunities/index.php

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of New Haven; nothing here affects any
other school's script.

Link check (ok): 3 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_200_job_posts.csv (school_id, post_link).
Checkpointed to school_id_200_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The job-opportunities page embeds newhaven.hrmdirect.com in a frame; its
list (job-openings.php) is read directly. Postings are job-opening.php?req=<n>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 200
SCHOOL_NAME = 'University of New Haven'
CAREERS_LINK = 'https://www.newhaven.edu:443/about/employment/job-opportunities/index.php'
ATS_PLATFORM = 'own website'

BOARD = 'https://newhaven.hrmdirect.com/employment/'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(BOARD + 'job-openings.php?sort=td&search=true&nohd=&dept=-1&city=-1&state=-1', timeout=40)
    if status != 200:
        raise RuntimeError(f'job openings status={status}')
    return [f'{BOARD}job-opening.php?req={r}&&#job' for r in dict.fromkeys(re.findall(r'job-opening\.php\?req=(\d+)', html))]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
