"""
Job postings scraper for school_id 1361 - McMurry University (US)
ATS platform: BambooHR
Careers link: https://mcm.edu/careers-at-mcmurry-university/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.
detect_platform does not know BambooHR and only this one school in
schools_master uses it, so the logic lives here rather than in the library.

The careers link was https://oncampusdining.com/mcm/job-opportunities/ --
the site of the university's FOOD SERVICE contractor, listing its dining
vacancies rather than McMurry's own hiring.

McMurry's careers page embeds BambooHR via a script tag, so the openings are
never in that page's HTML. BambooHR publishes them as JSON at
/careers/list, which needs no auth: 17 postings, "Adjunct Faculty Pool" and
"Dual Credit Adjunct" among them, each addressable at /careers/<id>.

Writes school_job_posts/school_id_1361_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1361_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
McMurry's careers page lists its BambooHR postings (user, 2026-10-20; the old link was the dining contractor's).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1361
SCHOOL_NAME = 'McMurry University'
CAREERS_LINK = 'https://mcm.edu/careers-at-mcmurry-university/'
ATS_PLATFORM = 'BambooHR'

LIST_API = 'https://mcmurry.bamboohr.com/careers/list'

POSTING_RE = re.compile(r'^https://mcmurry\.bamboohr\.com/careers/\d+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True, wait_ms=7000)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
