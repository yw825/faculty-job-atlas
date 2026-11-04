"""
Job postings scraper for school_id 1839 - Lingnan University (Hong Kong)
ATS platform: Cornerstone OnDemand (detected: cornerstone)
Careers link: https://lingnan.csod.com/ux/ats/careersite/4/home?c=lingnan&cfdd[0][id]=151&cfdd[0][options][0]=101

Lingnan University runs on a shared ATS platform -- every school on cornerstone uses the
exact same underlying site software, so this calls the shared
job_postings_lib.scrape_cornerstone adapter rather than duplicating
platform-specific API logic here. If results for this ONE school still need
a tweak that shouldn't apply to every cornerstone school, override find_links
below instead of editing the shared adapter.

Writes school_job_posts/school_id_1839_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1839_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Cornerstone board read with the shared adapter; its links
(.../careersite/4/requisition/<id>) open a LOGIN page, so each is stored in
the public form .../careersite/4/home/requisition/<id>?c=lingnan (the form
of the audit's example).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1839
SCHOOL_NAME = 'Lingnan University'
CAREERS_LINK = 'https://lingnan.csod.com/ux/ats/careersite/4/home?c=lingnan&cfdd[0][id]=151&cfdd[0][options][0]=101'
ATS_PLATFORM = 'Cornerstone OnDemand'
PLATFORM = 'cornerstone'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for url in lib.PLATFORM_ADAPTERS[PLATFORM](CAREERS_LINK, SCHOOL_NAME):
        m = re.search(r'/careersite/(\d+)/(?:home/)?requisition/(\d+)', url)
        url = f'https://lingnan.csod.com/ux/ats/careersite/{m.group(1)}/home/requisition/{m.group(2)}?c=lingnan' if m else url
        if url not in links:
            links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
