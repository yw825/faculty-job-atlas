"""
Job postings scraper for school_id 590 - Johns Hopkins University
ATS platform: own website
Careers link: https://facultyjobs.jhu.edu/positions

facultyjobs.jhu.edu renders client-side; the old link collected six
navigation entries and no jobs.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 590
SCHOOL_NAME = 'Johns Hopkins University'
CAREERS_LINK = 'https://facultyjobs.jhu.edu/positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# The faculty site is a Vue app: a plain fetch returns a 694-byte shell, which
# is why this school sat at six navigation links. It is backed by a public
# paginated JSON API carrying every posting -- 240 across 13 pages.
API = 'https://facultyjobs.jhu.edu/api/positions?page={page}'
MAX_PAGES = 40


def find_links():
    links, page, total_pages = [], 1, None
    while page <= MAX_PAGES:
        status, body = lib.fetch_static(API.format(page=page),
                                        extra_headers={'Accept': 'application/json'})
        if status != 200 or not body:
            break
        import json
        result = (json.loads(body).get('result') or {})
        positions = result.get('positions') or []
        if not positions:
            break
        for p in positions:
            pid = p.get('legacyPositionId') or p.get('id')
            if pid:
                links.append(f'https://apply.interfolio.com/{pid}')
        total_pages = result.get('totalPages') or 1
        if page >= total_pages:
            break
        page += 1
    if not links:
        raise RuntimeError('johns hopkins api returned no positions')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
