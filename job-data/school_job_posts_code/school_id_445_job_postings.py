"""
Job postings scraper for school_id 445 - University of Notre Dame
ATS platform: own website
Careers link: https://facultypositions.nd.edu/

SmartRecruiters carries Notre Dame's staff jobs, not its faculty openings.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 445
SCHOOL_NAME = 'University of Notre Dame'
CAREERS_LINK = 'https://facultypositions.nd.edu/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# Notre Dame runs SmartRecruiters for staff and Interfolio for faculty. The
# SmartRecruiters board (160 links) carries no faculty postings, so this reads
# the university's own faculty page, which lists every Interfolio opening.
LISTING = 'https://facultypositions.nd.edu/'
RENDER_WAIT_MS = 9000


def find_links():
    html = lib.fetch_rendered(LISTING, wait_ms=RENDER_WAIT_MS)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    ids = sorted(set(re.findall(r'apply\.interfolio\.com/(\d+)', html)), key=int)
    if not ids:
        raise RuntimeError('notre dame faculty page listed no positions')
    return [f'https://apply.interfolio.com/{i}' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
