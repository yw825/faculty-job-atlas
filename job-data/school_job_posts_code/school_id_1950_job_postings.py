"""
Job postings scraper for school_id 1950 - SUNY-Alfred State College (US)
ATS platform: InterviewExchange
Careers link: https://alfredstate.interviewexchange.com/static/clients/481ASM1/index.jsp

InterviewExchange board (or one of its categories); job ids collected and the advert address rebuilt.

Writes school_job_posts/school_id_1950_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1950_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1950
SCHOOL_NAME = "SUNY-Alfred State College"
CAREERS_LINK = 'https://alfredstate.interviewexchange.com/static/clients/481ASM1/index.jsp'
ATS_PLATFORM = 'InterviewExchange'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_interviewexchange(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
