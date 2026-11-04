"""
Job postings scraper for school_id 165 - University of Colorado-Colorado Springs (US)
Careers link: https://cu.taleo.net/careersection/2/moresearch.ftl?lang=en&location=6300103016&portal=101430233&radius=1&radiusType=K&searchExpanded=true

TUNED FIND_LINKS
One of the University of Colorado campuses on the CU system Taleo board
(cu.taleo.net): Anschutz Medical Campus (Aurora), Denver and Colorado
Springs share it, each with its own school_id; CU Boulder (162) has its own
site. This campus's postings are the board's jobs located in its city, plus
"Multiple Locations"/"Hybrid" jobs whose text opens with the campus name
(lib.scrape_cu_campus). Until 2026-10-12 ids 165 and 168 read
jobs.colorado.edu, which is Boulder's board, so they listed Boulder's jobs.
A posting is jobdetail.ftl?job=<job number>.

Writes school_job_posts/school_id_165_job_posts.csv (school_id, post_link).
Checkpointed to school_id_165_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 165
SCHOOL_NAME = 'University of Colorado-Colorado Springs'
CAREERS_LINK = 'https://cu.taleo.net/careersection/2/moresearch.ftl?lang=en&location=6300103016&portal=101430233&radius=1&radiusType=K&searchExpanded=true'
ATS_PLATFORM = 'Taleo (CU system)'
CAMPUS = 'colorado_springs'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_cu_campus(CAMPUS)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
