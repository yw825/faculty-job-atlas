"""
Job postings scraper for school_id 1504 - Saint Michael's College (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://stmichaels-ibukjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2

Saint Michael's College runs on a shared ATS platform, so this calls the
shared job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below and
pass it to run_checkpointed instead of editing the shared adapter.

The careers link was the college's HR landing page, which links out to the
board rather than listing anything. The generic word filter kept two of its
navigation links -- /outcomes/career-education/ and
/faculty-and-staff-resources/ -- and both reached the map as postings
titled "Henry 'Bud' Boucher, Jr. '69 Career Education Center" and
"Faculty & Staff Resources".

The board is the college's own Oracle tenant, linked from that HR page. It
returns 9 postings.

Writes school_job_posts/school_id_1504_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1504_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1504
SCHOOL_NAME = "Saint Michael's College"
CAREERS_LINK = ('https://stmichaels-ibukjb.fa.ocs.oraclecloud.com/hcmUI/'
                'CandidateExperience/en/sites/CX_2')
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

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
