"""
Job postings scraper for school_id 247 - Florida International University (US)
ATS platform: own website
Careers link: https://search.careers.fiu.edu/?role=employee&sort=newest

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Florida International University; nothing here affects any
other school's script.

Link check (ok): 13 posting-shaped links found -- rendered.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_247_job_posts.csv (school_id, post_link).
Checkpointed to school_id_247_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
FIU's job search page loads every posting from its own JSON service
(search.careers.fiu.edu/api/jobs, ~790 postings); the page shows 12 and
"Show more" buttons. A posting is the service's public URL
(pslinks.fiu.edu ... JobOpeningId=<n>).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 247
SCHOOL_NAME = 'Florida International University'
CAREERS_LINK = 'https://search.careers.fiu.edu/?role=employee&sort=newest'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, text = lib.fetch_static('https://search.careers.fiu.edu/api/jobs', timeout=60)
    if status != 200:
        raise RuntimeError(f'FIU jobs service status={status}')
    return list(dict.fromkeys(j['URL'] for j in json.loads(text)['JOB_POSTINGS'] if j.get('URL')))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
