"""
Job postings scraper for school_id 1919 - University of Connecticut-Farmington (UConn Health) (US)
Careers link: https://jobs.hr.uconn.edu/en-us/filter/?search-keyword=&location=UConn%20Health%20(Farmington)

TUNED FIND_LINKS
One of the University of Connecticut campuses: UConn has a single PageUp
board (jobs.hr.uconn.edu) with a "location" filter, and each campus has its
own school_id (Storrs, Avery Point, Stamford, Waterbury, Hartford,
Farmington/UConn Health; there is no general "University of Connecticut"
entry). This campus takes its filter values -- see lib.UCONN_CAMPUS; Storrs
takes every value no other campus claims. A posting is /en-us/job/<id>/<slug>.

Writes school_job_posts/school_id_1919_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1919_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1919
SCHOOL_NAME = 'University of Connecticut-Farmington (UConn Health)'
CAREERS_LINK = 'https://jobs.hr.uconn.edu/en-us/filter/?search-keyword=&location=UConn%20Health%20(Farmington)'
ATS_PLATFORM = 'PageUp'
CAMPUS = 'farmington'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_uconn_campus(CAMPUS)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
