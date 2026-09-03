"""
Job postings scraper for school_id 1844 - The Hong Kong Polytechnic University (Hong Kong)
ATS platform: own website
Careers link: https://jobs.polyu.edu.hk/academic.php

CUSTOMIZED (confirmed live): postings are rows in a results table where
the whole row is made clickable via JS reading a data-href attribute
(<tr class="ITS_clickableTableRow" data-href="job_detail.php?job=...">) --
there is no real <a href> anywhere on these rows at all, which is why the
generic default (href/text-based) found nothing. Confirmed live: 55 real
postings on this page alone once read from data-href instead.

Writes school_job_posts/school_id_1844_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1844_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1844
SCHOOL_NAME = 'The Hong Kong Polytechnic University'
CAREERS_LINK = 'https://jobs.polyu.edu.hk/academic.php'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for row in soup.find_all('tr', attrs={'data-href': True}):
        full = lib.urljoin(CAREERS_LINK, row['data-href'])
        if full not in seen:
            seen.add(full)
            links.append(full)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
