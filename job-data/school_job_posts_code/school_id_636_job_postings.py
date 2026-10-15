"""
Job postings scraper for school_id 636 - Wayne State University (US)
ATS platform: Cornerstone OnDemand (detected: cornerstone)
Careers link: https://waynetalent.csod.com/ux/ats/careersite/2/home?c=waynetalent

Wayne State University runs on a shared ATS platform -- every school on cornerstone uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_cornerstone adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every cornerstone school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_636_job_posts.csv (school_id, post_link).
Checkpointed to school_id_636_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Read with the career site's own search request; postings stored in the
.../home/requisition/<id>?c=waynetalent form (the bare /requisition/<id>
address opens the site's welcome page).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 636
SCHOOL_NAME = 'Wayne State University'
CAREERS_LINK = 'https://waynetalent.csod.com/ux/ats/careersite/2/home?c=waynetalent'
ATS_PLATFORM = 'Cornerstone OnDemand'
PLATFORM = 'cornerstone'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_cornerstone_site(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
