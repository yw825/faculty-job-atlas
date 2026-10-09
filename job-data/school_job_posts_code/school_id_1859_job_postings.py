"""
Job postings scraper for school_id 1859 - Singapore Management University (Singapore)
Careers link: https://smucareers.taleo.net/careersection/smu_ext_ft/jobsearch.ftl

TUNED FIND_LINKS
SMU's job board is Taleo (career section smu_ext_ft), the corrected link in
the audit sheet; read with the shared Taleo reader, which pages through the
search results. Postings are jobdetail.ftl?job=<number>. The old link,
careers.smu.edu.sg/faculty-recruitment, did not carry the board's jobs.

Writes school_job_posts/school_id_1859_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1859_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1859
SCHOOL_NAME = 'Singapore Management University'
CAREERS_LINK = 'https://smucareers.taleo.net/careersection/smu_ext_ft/jobsearch.ftl'
ATS_PLATFORM = 'Taleo'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_taleo(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
