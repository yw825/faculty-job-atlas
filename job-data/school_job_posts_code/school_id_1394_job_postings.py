"""
Job postings scraper for school_id 1394 - Rice University (US)
ATS platform: own website (Interfolio links published on Rice's own page)
Careers link: https://vpaa.rice.edu/faculty/open-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

Rice publishes each faculty search as a direct apply.interfolio.com link on
its own page, so the postings are harvested from that page rather than from
the Interfolio board API. The generic COMMON_JOB_URL_HINTS filter found only
4 links here because an Interfolio URL is nothing but a number -- it carries
no "job"/"career"/"position" word for the href pattern to match, and the
anchor text is the search title. Matching the apply.interfolio.com URL shape
directly finds 26.

Note these are already public per-posting URLs, so they need no
legacy_position_id translation -- that trap applies only to ids read from a
board's own API, not to links a university publishes itself.

Writes school_job_posts/school_id_1394_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1394_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1394
SCHOOL_NAME = 'Rice University'
CAREERS_LINK = 'https://vpaa.rice.edu/faculty/open-positions'
ATS_PLATFORM = 'own website'

POSTING = re.compile(r'https://apply\.interfolio\.com/\d+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=8000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    links = sorted(set(POSTING.findall(html)))
    if not links:
        raise RuntimeError('rice open-positions page listed no interfolio links')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
