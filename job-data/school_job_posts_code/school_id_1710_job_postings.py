"""
Job postings scraper for school_id 1710 - University of Milan (Italy)
ATS platform: own website
Careers link: https://www.unimi.it/en/university/work-us/calls-and-competitions

CUSTOMIZED (confirmed live): postings are titled "Bando ..." (Italian for
"call/notice") with hrefs containing "bando"/"concorso"/"selezione",
none of which are job-shaped keywords the generic default's (English)
filter looks for.

Writes school_job_posts/school_id_1710_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1710_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1710
SCHOOL_NAME = 'University of Milan'
CAREERS_LINK = 'https://www.unimi.it/en/university/work-us/calls-and-competitions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

POSTING_RE = re.compile(r'bando|concorso|selezione', re.I)


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK, href_pattern=POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
