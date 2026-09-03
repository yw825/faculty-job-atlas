"""
Job postings scraper for school_id 1707 - University of Bologna (Italy)
ATS platform: own website
Careers link: https://bandi.unibo.it/didattica/incarichi-insegnamento

CUSTOMIZED (confirmed live): the original careers_link
(unibo.it/.../docenti-e-ricercatori-1) was timing out on every fetch
attempt; this replacement URL, given directly, works and lists real
postings under bandi.unibo.it/s/<department>/<slug> -- a pattern the
generic default's job-shaped filter doesn't match (Italian bando/bandi
titles, no English job-shaped keyword).

Writes school_job_posts/school_id_1707_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1707_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1707
SCHOOL_NAME = 'University of Bologna'
CAREERS_LINK = 'https://bandi.unibo.it/didattica/incarichi-insegnamento'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

POSTING_RE = re.compile(r'bandi\.unibo\.it/s/')


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
