"""
Job postings scraper for school_id 1904 - NEOMA Business School (France)
ATS platform: own website (Interfolio links published on NEOMA's own page)
Careers link: https://neoma-bs.com/offres_emploi

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Same shape as Rice (school_id 1394): NEOMA publishes each faculty search as
a direct apply.interfolio.com link on its own vacancies page rather than
running a public Interfolio board of its own. The generic
COMMON_JOB_URL_HINTS filter is useless here because an Interfolio URL is
nothing but a number -- it carries no "job"/"career"/"position" word for the
href pattern to match. Matching the apply.interfolio.com URL shape directly
is what finds them.

These are already public per-posting URLs, so they need no
legacy_position_id translation -- that trap applies only to ids read from a
board's own API, not to links a school publishes itself.

The page is static, so no render is needed. At the time of writing this
yields 7 postings, all professorial ("Full-time, permanent Assistant /
Associate / Full Professor" in Operations, Strategy, and others).

Writes school_job_posts/school_id_1904_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1904_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1904
SCHOOL_NAME = 'NEOMA Business School'
CAREERS_LINK = 'https://neoma-bs.com/offres_emploi'
ATS_PLATFORM = 'own website'

POSTING = re.compile(r'https://apply\.interfolio\.com/\d+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=20)
    if status != 200 or not html:
        raise RuntimeError(f'neoma vacancies page returned http={status}')
    links = sorted(set(POSTING.findall(html)))
    if not links:
        raise RuntimeError('neoma vacancies page listed no interfolio links')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
