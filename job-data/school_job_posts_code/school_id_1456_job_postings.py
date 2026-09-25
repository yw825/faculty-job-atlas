"""
Job postings scraper for school_id 1456 - Randolph-Macon College (US)
ATS platform: ADP Workforce Now (detected: adp)
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=0885b537-c9f5-47f8-aa4f-0ad7bbebf412

Randolph-Macon College runs on a shared ATS platform, so this calls the
shared job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here.

The careers link was the college's own HR "employment opportunities" page,
which links OUT to its ADP board rather than listing anything itself, so a
structural scrape of that page found no postings. The board's account id
sits in the link on that page; ADP's public API answers with 6 requisitions
for it.

Writes school_job_posts/school_id_1456_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1456_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1456
SCHOOL_NAME = 'Randolph-Macon College'
CAREERS_LINK = ('https://workforcenow.adp.com/mascsr/default/mdf/recruitment/'
                'recruitment.html?cid=0885b537-c9f5-47f8-aa4f-0ad7bbebf412')
ATS_PLATFORM = 'ADP Workforce Now'
PLATFORM = 'adp'

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
