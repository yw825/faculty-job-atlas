"""
Job postings scraper for school_id 1502 - University of Vermont (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://www.uvmjobs.com/

University of Vermont runs on a shared ATS platform, so this calls the
shared job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here.

The careers link was www.uvm.edu/human-resources/careers, an HR information
page that describes how to apply and links onward, so the school recorded
two navigation links. UVM's board is www.uvmjobs.com -- a PeopleAdmin
tenant on a vanity domain rather than the usual <label>.peopleadmin.com,
which is why subdomain guessing never reached it. Its feed lists 98
postings.

Writes school_job_posts/school_id_1502_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1502_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1502
SCHOOL_NAME = 'University of Vermont'
CAREERS_LINK = 'https://www.uvmjobs.com/'
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
