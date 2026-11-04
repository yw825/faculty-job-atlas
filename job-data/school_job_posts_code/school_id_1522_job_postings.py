"""
Job postings scraper for school_id 1522 - Whitworth University
ATS platform: SchoolJobs (NeoGov) (detected: schooljobs)
Careers link: https://www.whitworth.edu/cms/administration/human-resource-services/faculty-lecturer-employment-opportunities/

Whitworth University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_schooljobs adapter rather than duplicating
platform-specific logic here.

The previous careers link did not reach this board -- it pointed at a careers landing page, a staff-only board or another
university's board
so the school collected navigation links or nothing at all. This board was
verified live on 2026-09-24 and returned 4 postings.

If results for THIS ONE school need a tweak that shouldn't apply to every
schooljobs school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_1522_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1522_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1522
SCHOOL_NAME = 'Whitworth University'
CAREERS_LINK = 'https://www.whitworth.edu/cms/administration/human-resource-services/faculty-lecturer-employment-opportunities/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# Whitworth lists faculty openings on this page itself (adverts link out to
# its SchoolJobs board, Interfolio or a PDF). Its SchoolJobs board is staff
# only, which is why this school used to hold custodian/admin links. An
# empty page is a real answer: no faculty openings.
POSTING_RE = re.compile(r'(?i)schooljobs\.com/careers/whitworth/jobs/\d+|apply\.interfolio\.com/\d+|'
                        r'whitworth\.edu/.*\.pdf$')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=4000)
    return sorted({u for u in lib.extract_links(html, CAREERS_LINK) if POSTING_RE.search(u)})


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
