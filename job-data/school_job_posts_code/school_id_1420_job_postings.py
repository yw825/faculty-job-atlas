"""
Job postings scraper for school_id 1420 - Angelo State University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://employment.angelo.edu/

Angelo State University runs on a shared ATS platform, so this calls the
shared job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here.

The careers link was www.angelo.edu/work-at-asu/, a recruitment marketing
page that links to benefits and "why work here" content rather than to
openings, so the scraper collected four navigation links and no postings.
The university's board is employment.angelo.edu, whose Atom feed lists 61.

Nothing on the old page pointed at that hostname -- it was found by trying
the usual board subdomains directly, which is also how Lincoln Memorial's
and St Lawrence's boards turned up.

Writes school_job_posts/school_id_1420_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1420_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1420
SCHOOL_NAME = 'Angelo State University'
CAREERS_LINK = 'https://employment.angelo.edu/'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
