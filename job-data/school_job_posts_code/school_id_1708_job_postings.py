"""
Job postings scraper for school_id 1708 - Bocconi University (Italy)
Careers link: https://jobmarket.unibocconi.eu/

TUNED FIND_LINKS
Bocconi's own faculty job market (jobmarket.unibocconi.eu) lists every
faculty call -- assistant, associate and full professor -- as a table row
<tr id="N"> with "ID N / Publication / Deadline", the position and the
department; each call is jobmarket.unibocconi.eu/?id=N. The table also keeps
calls whose deadline has passed, so only rows with a deadline of today or
later are collected (the user's note on this school). The national MUR
portal, used 2026-10-09 morning, carried only 1 of Bocconi's ~30 calls:
as a private university Bocconi hires internationally outside it.

Writes school_job_posts/school_id_1708_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1708_job_postings.checkpoint next to this script.
"""
import datetime as dt
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib
from bs4 import BeautifulSoup

SCHOOL_ID = 1708
SCHOOL_NAME = 'Bocconi University'
CAREERS_LINK = 'https://jobmarket.unibocconi.eu/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=40)
    if status != 200:
        raise RuntimeError(f'job market status={status}')
    today = dt.date.today()
    links = []
    for tr in BeautifulSoup(html, 'html.parser').find_all('tr', id=re.compile(r'^\d+$')):
        m = re.search(r'Deadline\s*(\d{2})/(\d{2})/(\d{4})', tr.get_text(' ', strip=True))
        if m and dt.date(int(m[3]), int(m[2]), int(m[1])) < today:
            continue
        links.append(f'https://jobmarket.unibocconi.eu/?id={tr["id"]}')
    if not links and 'Deadline' not in html:
        raise RuntimeError('job market table not found')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
