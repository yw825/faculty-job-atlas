"""
Job postings scraper for school_id 1100 - Oklahoma State University-Stillwater (US)
ATS platform: own website
Careers link: https://jobs.okstate.edu/jobs/search/search-page-oklahoma-state?page=1&employment_type_uids%5B%5D=5c5da7ec2907fcbb8822ceda56aa53d0&employment_type_uids%5B%5D=369d5b24d91990b57f28e9ebbee41ffa&dropdown_field_2_uids%5B%5D=a995ee9d3e791bb4266bea380bedb381

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Oklahoma State University-Main Campus; nothing here affects any
other school's script.

Link check (ok): 39 posting-shaped links found -- rendered.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1100_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1100_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
OSU system board (jobs.okstate.edu): the link's employment-type and Posting Campus
filters are kept; pages walked.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1100
SCHOOL_NAME = "Oklahoma State University-Stillwater"
CAREERS_LINK = 'https://jobs.okstate.edu/jobs/search/search-page-oklahoma-state?page=1&employment_type_uids%5B%5D=5c5da7ec2907fcbb8822ceda56aa53d0&employment_type_uids%5B%5D=369d5b24d91990b57f28e9ebbee41ffa&dropdown_field_2_uids%5B%5D=a995ee9d3e791bb4266bea380bedb381'
ATS_PLATFORM = 'own website'

POSTING_RE = re.compile(r'^https://jobs\.okstate\.edu/jobs/(?!search)[a-z0-9-]+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_paged_board(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
