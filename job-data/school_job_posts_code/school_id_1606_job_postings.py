"""
Job postings scraper for school_id 1606 - Crandall University (Canada)
ATS platform: own website
Careers link: https://www.crandallu.ca/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Crandall University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is a PDF ad under /crandallwp20/wp-content/uploads/<yyyy>/<mm>/.
The site's firewall rejects the shared library's dated user agent with 403,
so the page is fetched with BROWSER_UA (the info script does the same for
the PDFs).

Writes school_job_posts/school_id_1606_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1606_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1606
SCHOOL_NAME = 'Crandall University'
CAREERS_LINK = 'https://www.crandallu.ca/employment/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# This site's firewall answers 403 to the shared library's "Chrome/120" user
# agent (any current one passes), so this school sends its own.
BROWSER_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
POSTING_RE = re.compile(r'^https://www\.crandallu\.ca/crandallwp20/wp-content/uploads/\d{4}/\d{2}/[^/?#]+\.pdf$', re.I)


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30, extra_headers={'User-Agent': BROWSER_UA})
    if status != 200:
        raise RuntimeError(f'crandall employment page status={status}')
    return [u for u in lib.extract_links(html, CAREERS_LINK) if POSTING_RE.search(u)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
