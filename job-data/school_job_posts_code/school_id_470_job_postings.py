"""
Job postings scraper for school_id 470 - McPherson College (US)
ATS platform: own website
Careers link: https://my.mcpherson.edu/ICS/Employment/Employment_Landing_Page.jnz?portlet=Employment_Position_Application

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for McPherson College; nothing here affects any
other school's script.

Link check (review): 2 posting-shaped links found -- rendered few job-shaped links.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_470_job_posts.csv (school_id, post_link).
Checkpointed to school_id_470_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
A Jenzabar positions table: rows appear once "Search positions" is pressed
and open by postback, so each is stored as the page plus #<title slug>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 470
SCHOOL_NAME = 'McPherson College'
CAREERS_LINK = 'https://my.mcpherson.edu/ICS/Employment/Employment_Landing_Page.jnz?portlet=Employment_Position_Application'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [f'{CAREERS_LINK}#{row[0]}' for row in lib.jenzabar_positions(CAREERS_LINK)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
