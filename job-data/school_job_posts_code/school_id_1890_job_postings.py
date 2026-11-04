"""
Job postings scraper for school_id 1890 - University of Gothenburg (Sweden)
ATS platform: own website
Careers link: https://www.gu.se/en/work-at-the-university-of-gothenburg/vacancies

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Gothenburg; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1890_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1890_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Gothenburg's vacancies are on ReachMee: the list page
main?site=7&lang=UK&validator=<key> has them all and a posting is
job?site=7&lang=UK&validator=<key>&job_id=<n>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1890
SCHOOL_NAME = 'University of Gothenburg'
CAREERS_LINK = 'https://www.gu.se/en/work-at-the-university-of-gothenburg/vacancies'
ATS_PLATFORM = 'own website'

REACHMEE = 'https://web103.reachmee.com/ext/I005/1035/'
QUERY = 'site=7&lang=UK&validator=9b89bead79bb7258ad55c8d75228e5b7'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(f'{REACHMEE}main?{QUERY}', timeout=40)
    if status != 200:
        raise RuntimeError(f'ReachMee list status={status}')
    ids = list(dict.fromkeys(re.findall(r'(?:job_id|rmjob)=(\d+)', html)))
    return [f'{REACHMEE}job?{QUERY}&job_id={i}' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
