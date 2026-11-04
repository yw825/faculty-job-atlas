"""
Job postings scraper for school_id 1654 - Université du Québec à Trois-Rivières (Canada)
ATS platform: own website
Careers link: https://atlas.workland.com/careers/uqtr/jobs?page=1

CUSTOMIZED (confirmed live): a Workland-hosted job board (mostly French-
language postings, "[FR]: ..." titles) needing a longer render wait than
the generic default's 2s (a "Loading the list of jobs... Please wait..."
placeholder shows first) and whose "page 2" pagination link is
href="#"/JS-only, with a cookie-consent overlay that has to be dismissed
first or it intercepts the click. Confirmed live: 12 postings on page 1,
1 more on page 2 (13 total).

TUNED FIND_LINKS
Each opening is atlas.workland.com/work/<id>/<slug>; the UQTR board
paginates (?page=N), renders slowly, and is walked until a page adds nothing.

Writes school_job_posts/school_id_1654_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1654_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1654
SCHOOL_NAME = 'Université du Québec à Trois-Rivières'
CAREERS_LINK = 'https://atlas.workland.com/careers/uqtr/jobs?page=1'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def _work_links(html, base_url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return [lib.urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)
            if a['href'].startswith('/work/')]


POSTING_RE = re.compile(r'^https://atlas\.workland\.com/work/\d+/[^/?#]+$', re.I)


POSTING_RE = re.compile(r'^https://atlas\.workland\.com/work/\d+/[^/?#]+', re.I)


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE, wait_ms=8000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
