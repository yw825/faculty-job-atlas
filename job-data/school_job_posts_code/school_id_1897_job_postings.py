"""
Job postings scraper for school_id 1897 - Manhattan University (US)
ATS platform: own website
Careers link: https://www.schooljobs.com/careers/manhattanedu/FTFaculty

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Manhattan University; nothing here affects any
other school's script.

Link check (ok): 13 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1897_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1897_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
NEOGOV board read from its list service. The board's jobType filter only
matches a type's full name, so a link filtered on "Faculty" can show 0 jobs
while "Adjunct Faculty" postings are open; the filter is applied as meant
(exact type first, otherwise types/categories containing the word).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1897
SCHOOL_NAME = 'Manhattan University'
CAREERS_LINK = 'https://www.schooljobs.com/careers/manhattanedu/FTFaculty'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# Full-time faculty and adjunct faculty are separate SchoolJobs job-interest
# boards; the parent board also lists staff.
ADJUNCT = 'https://www.schooljobs.com/careers/manhattanedu/AdjunctFaculty'


def find_links():
    links = lib.scrape_neogov_filtered(CAREERS_LINK)
    return links + [u for u in lib.scrape_neogov_filtered(ADJUNCT) if u not in links]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
