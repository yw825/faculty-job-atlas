"""
Job postings scraper for school_id 1893 - University of Vaasa (Finland)
ATS platform: Finnish gov recruitment portal
Careers link: https://uva.rekrytointi.com/paikat/?o=A_LOJ&list=6&lang=en

CUSTOMIZED (confirmed live): same rekrytointi.com (Finnish recruitment
portal, laura.fi) platform as school_id 1671 (Hanken School of Economics)
-- see that script's docstring. Postings are plain links with a
"jid=<id>" job-id query param, which doesn't contain any word the generic
default's job-shaped filter looks for -- confirmed live, the page's own
"Open jobs: 3" count matched exactly once filtered on that param instead.

Writes school_job_posts/school_id_1893_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1893_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1893
SCHOOL_NAME = 'University of Vaasa'
CAREERS_LINK = 'https://uva.rekrytointi.com/paikat/?o=A_LOJ&list=6&lang=en'
ATS_PLATFORM = 'Finnish gov recruitment portal'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

JOB_ID_RE = re.compile(r'[?&]jid=\d+')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK, href_pattern=JOB_ID_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
