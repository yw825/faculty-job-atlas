"""
Job postings scraper for school_id 322 - Chaminade University of Honolulu (US)
ATS platform: ADP (detected: adp)
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=052b3ffb-78d8-40ac-bd43-f6ee902354e2&ccId=2543893806_3653&lang=en_US

Chaminade University of Honolulu runs on a shared ATS platform -- every school on adp uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every adp school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_322_job_posts.csv (school_id, post_link).
Checkpointed to school_id_322_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 322
SCHOOL_NAME = 'Chaminade University of Honolulu'
CAREERS_LINK = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=052b3ffb-78d8-40ac-bd43-f6ee902354e2&ccId=2543893806_3653&lang=en_US'
ATS_PLATFORM = 'ADP'
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
