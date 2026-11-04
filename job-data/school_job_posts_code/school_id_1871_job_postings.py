"""
Job postings scraper for school_id 1871 - Nottingham Trent University (United Kingdom)
ATS platform: own website
Careers link: https://vacancies.ntu.ac.uk/Home/Job

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Nottingham Trent University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1871_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1871_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to NTU's own board (same software as
Manchester's): cards load 12 at a time from /Home/_JobCard?Skip=N. The old
jobs.ac.uk keyword search also returned other universities' adverts.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1871
SCHOOL_NAME = 'Nottingham Trent University'
CAREERS_LINK = 'https://vacancies.ntu.ac.uk/Home/Job'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    host = re.match(r'https?://[^/]+', CAREERS_LINK).group(0)
    ids = []
    for skip in range(0, 2400, 12):
        status, html = lib.fetch_static(f'{host}/Home/_JobCard?Skip={skip}', timeout=40)
        if status != 200:
            if skip == 0:
                raise RuntimeError(f'job cards status={status}')
            break
        new = list(dict.fromkeys(i for i in re.findall(r'JobDetail\?JobId=(\d+)', html) if i not in ids))
        if not new:
            break
        ids += new
    return [f'{host}/Job/JobDetail?JobId={i}' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
