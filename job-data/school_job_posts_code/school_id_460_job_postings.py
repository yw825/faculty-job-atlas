"""
Job postings scraper for school_id 460 - Emporia State University (US)
ATS platform: own website
Careers link: https://hr.hornet365.com/open-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Emporia State University; nothing here affects any
other school's script.

Link check (review): 1 posting-shaped links found -- rendered few job-shaped links.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_460_job_posts.csv (school_id, post_link).
Checkpointed to school_id_460_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The open-positions page links each opening by its upper-case title to a
page at the site root.
The open-positions page lists each opening in a table, linked by its
title to a page at the site root (the site menu shares that link shape).
The open-positions page lists each opening in a table, linked by its
title to a page at the site root (the site menu shares that link shape).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 460
SCHOOL_NAME = 'Emporia State University'
CAREERS_LINK = 'https://hr.hornet365.com/open-positions'
ATS_PLATFORM = 'own website'

SKIP = ('/password-help', '/open-positions')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    soup = BeautifulSoup(lib._fetch_rendered_retry(CAREERS_LINK, 5000), 'html.parser')
    links = [urljoin(CAREERS_LINK, a['href']) for a in soup.select('div.table-wrapper a[href]') if re.fullmatch(r'/[a-z0-9-]+', a['href'])]
    return list(dict.fromkeys(links))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
