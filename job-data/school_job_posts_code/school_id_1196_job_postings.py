"""
Job postings scraper for school_id 1196 - Carlow University (US)
ATS platform: own website
Careers link: https://www.carlow.edu/about/employment/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Carlow University; nothing here affects any
other school's script.

Link check (review): 0 posting-shaped links found -- rendered no job-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1196_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1196_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers page embeds a Paycor (Newton) board (?gnk=job&gni=<id> on the page is the
Paycor job id); the board itself is read.
The careers page holds a Paycor board in a frame; opened directly the board bounces
back to the school page, so the frame is read (lib.scrape_paycor_frame).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1196
SCHOOL_NAME = 'Carlow University'
CAREERS_LINK = 'https://www.carlow.edu/about/employment/'
ATS_PLATFORM = 'own website'

BOARD = 'https://recruitingbypaycor.com/career/CareerHome.action?clientId=8a7883d061f94ddb0162022ae9e952fc'

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
