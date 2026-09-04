"""
Job postings scraper for school_id 124 - University of the West (US)
ATS platform: ADP (detected: adp)
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=31cd0b73-92c3-4ed2-84f8-5a6de61f8f2c&ccId=19000101_000001&lang=en_US&source=CC2&selectedMenuKey=CurrentOpenings

University of the West runs on a shared ATS platform -- every school on adp uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every adp school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_124_job_posts.csv (school_id, post_link).
Checkpointed to school_id_124_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 124
SCHOOL_NAME = 'University of the West'
CAREERS_LINK = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=31cd0b73-92c3-4ed2-84f8-5a6de61f8f2c&ccId=19000101_000001&lang=en_US&source=CC2&selectedMenuKey=CurrentOpenings'
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
