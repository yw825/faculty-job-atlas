"""
Job postings scraper for school_id 1899 - Frankfurt School of Finance & Management (Germany)
Careers link: https://jobs.frankfurt-school.de/

Writes school_job_posts/school_id_1899_job_posts.csv. Checkpointed to
school_id_1899_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Staff jobs are on jobs.frankfurt-school.de (/en/jobs/<id>/<slug>; the /de/
duplicates and list page are dropped); faculty positions are posted on
Interfolio (board 31504, found 2026-10-09), which is read too.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1899
SCHOOL_NAME = 'Frankfurt School of Finance & Management'
CAREERS_LINK = 'https://jobs.frankfurt-school.de/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=40)
    if status != 200:
        raise RuntimeError(f'jobs status={status}')
    links = []
    for path in re.findall(r'href="(?:https://jobs\.frankfurt-school\.de)?(/en/jobs/\d+/[a-z0-9-]+)"', html):
        if 'https://jobs.frankfurt-school.de' + path not in links:
            links.append('https://jobs.frankfurt-school.de' + path)
    try:
        links += lib.scrape_interfolio('https://apply.interfolio.com/31504/positions')
    except RuntimeError:
        pass  # no faculty positions open
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
