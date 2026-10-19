"""
Job postings scraper for school_id 1174 - Lincoln University (US)
ATS platform: Paycor
Careers link: https://www.lincoln.edu/careers/index.html

The careers page embeds a Paycor (Newton) board (?gnk=job&gni=<id>); the board itself is read.

Writes school_job_posts/school_id_1174_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1174_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers page holds a Paycor board in a frame; opened directly the board bounces
back to the school page, so the frame is read (lib.scrape_paycor_frame).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1174
SCHOOL_NAME = "Lincoln University"
CAREERS_LINK = 'https://www.lincoln.edu/careers/index.html'
ATS_PLATFORM = 'Paycor'

BOARD = 'https://recruitingbypaycor.com/career/CareerHome.action?clientId=8a7882675311d7ae0153200a1b2b06d8'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paycor_frame(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
