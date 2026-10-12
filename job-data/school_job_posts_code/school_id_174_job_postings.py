"""
Job postings scraper for school_id 174 - University of Northern Colorado (US)
ATS platform: Cornerstone OnDemand (detected: cornerstone)
Careers link: https://unco.csod.com/ux/ats/careersite/1/home?c=unco

University of Northern Colorado runs on a shared ATS platform -- every school on cornerstone uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_cornerstone adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every cornerstone school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_174_job_posts.csv (school_id, post_link).
Checkpointed to school_id_174_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Cornerstone board read with the shared adapter; its links
(.../careersite/1/requisition/<id>) open a maintenance/login page, so each
is stored in the public form .../careersite/1/home/requisition/<id>?c=unco
(the form of the audit's example).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 174
SCHOOL_NAME = 'University of Northern Colorado'
CAREERS_LINK = 'https://unco.csod.com/ux/ats/careersite/1/home?c=unco'
ATS_PLATFORM = 'Cornerstone OnDemand'
PLATFORM = 'cornerstone'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for url in lib.PLATFORM_ADAPTERS[PLATFORM](CAREERS_LINK, SCHOOL_NAME):
        m = re.search(r'/careersite/(\d+)/(?:home/)?requisition/(\d+)', url)
        url = f'https://unco.csod.com/ux/ats/careersite/{m.group(1)}/home/requisition/{m.group(2)}?c=unco' if m else url
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
