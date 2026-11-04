"""
Job postings scraper for school_id 1057 - Ohio State University-Marion (US)
ATS platform: own website
Careers link: https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Ohio State University-Marion Campus; nothing here affects any
other school's script.

Link check (ok): 5 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_1057_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1057_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Ohio State's one Workday board (Academic + Post Doctoral groups). Marion has no
location filter value until it posts a job, so postings whose location path
names Marion are kept.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1057
SCHOOL_NAME = "Ohio State University-Marion"
CAREERS_LINK = 'https://osu.wd1.myworkdayjobs.com/OSUCareers?jobFamilyGroup=67612469e2ea01a29e348f105b01ff10&jobFamilyGroup=4636ab80487a01dbec7abc635c010515'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [u for u in lib.PLATFORM_ADAPTERS['workday'](CAREERS_LINK, SCHOOL_NAME) if re.search(r'/job/[^/]*Marion', u, re.I)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
