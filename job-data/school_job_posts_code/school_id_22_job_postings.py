"""
Job postings scraper for school_id 22 - Auburn University at Montgomery (US)
ATS platform: own website
Careers link: https://jobs.aum.edu/aum-careers-home/jobs?tags2=Faculty

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Auburn University at Montgomery; nothing here affects any
other school's script.

Link check (ok): 11 posting-shaped links found.

TUNED FIND_LINKS
This is an iCIMS "Jibe" site; the listing page renders 10 at a time, so
the JSON API behind it (/api/jobs) is read instead. jobs.auburn.edu and
jobs.aum.edu serve ONE shared Auburn-system feed -- both return the same 76
faculty jobs -- so the campus is pinned with tags1=AUM (tags1 is "Auburn"
for the main campus, "AUM" for Montgomery). Postings are stored as
/aum-careers-home/jobs/<req_id>?lang=en-us, the form already in the checkpoint.

Writes school_job_posts/school_id_22_job_posts.csv (school_id, post_link).
Checkpointed to school_id_22_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 22
SCHOOL_NAME = 'Auburn University at Montgomery'
CAREERS_LINK = 'https://jobs.aum.edu/aum-careers-home/jobs?tags2=Faculty'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


API = 'https://jobs.aum.edu/api/jobs'
CAMPUS_TAG = 'AUM'
POSTING_URL = 'https://jobs.aum.edu/aum-careers-home/jobs/{}?lang=en-us'


def find_links():
    import json
    links, page, total = [], 1, None
    while page <= 30:
        status, text = lib.fetch_static(
            f'{API}?tags2=Faculty&tags1={CAMPUS_TAG}&page={page}&limit=50', timeout=30)
        if status != 200:
            raise RuntimeError(f'jibe api status={status}')
        data = json.loads(text)
        total = data.get('totalCount', 0)
        jobs = data.get('jobs') or []
        for j in jobs:
            req = j.get('data', {}).get('req_id')
            if req and POSTING_URL.format(req) not in links:
                links.append(POSTING_URL.format(req))
        if not jobs or len(links) >= total:
            break
        page += 1
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
