"""
Job postings scraper for school_id 1248 - Universidad Politecnica de Puerto Rico (US)
ATS platform: ADP (detected: adp)
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=5388a0c5-18fe-449e-b500-098740269275&ccId=19000101_000001&type=JS&lang=en_US

Universidad Politecnica de Puerto Rico runs on a shared ATS platform -- every school on adp uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every adp school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 2 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Polytechnic University of Puerto Rico-Orlando.

Writes school_job_posts/school_id_1248_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1248_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1248
SCHOOL_NAME = 'Universidad Politecnica de Puerto Rico'
CAREERS_LINK = 'https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=5388a0c5-18fe-449e-b500-098740269275&ccId=19000101_000001&type=JS&lang=en_US'
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
