"""
Job postings scraper for school_id 1780 - University of New England (Australia)
ATS platform: own website
Careers link: https://www.une.edu.au/jobs-at-une/current-vacancies

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of New England; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1780_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1780_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
UNE's current-vacancies page embeds its HR system (hr.une.edu.au, WK8127);
the vacancy list is WK8127$APP.QueryList and each vacancy is
WK8127$APP.draw_attachments?P_VACANCY_REF_NO=<n> (the anchor the audit quotes).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1780
SCHOOL_NAME = 'University of New England'
CAREERS_LINK = 'https://www.une.edu.au/jobs-at-une/current-vacancies'
ATS_PLATFORM = 'own website'

BASE = 'https://hr.une.edu.au/ords/concept_ords/'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(BASE + 'WK8127$APP.QueryList?Z_ORDER_BY=1', timeout=40)
    if status != 200:
        raise RuntimeError(f'vacancy list status={status}')
    refs = list(dict.fromkeys(re.findall(r'P_VACANCY_REF_NO=(\d+)', html)))
    return [f'{BASE}WK8127$APP.draw_attachments?P_VACANCY_REF_NO={r}' for r in refs]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
