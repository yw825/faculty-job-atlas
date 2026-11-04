"""
Job postings scraper for school_id 346 - Graceland University-Lamoni (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://ibqcjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions

Graceland University-Lamoni runs on a shared ATS platform -- every school on
oracle uses the same underlying site software, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below and
pass it to run_checkpointed instead of editing the shared adapter.

The careers link was https://sfp.ocs.oraclecloud.com/graceland/portal/saml)
-- note the trailing parenthesis, a copy/paste artefact that had been stored
verbatim. Even with it removed that host is a SAML sign-in portal, not a job
board, and the adapter timed out waiting for a job request that never came.

Graceland's board is its own Oracle tenant, ibqcjb, found on the
university's employment page. It returns 16 postings.

Writes school_job_posts/school_id_346_job_posts.csv (school_id, post_link).
Checkpointed to school_id_346_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 346
SCHOOL_NAME = 'Graceland University-Lamoni'
CAREERS_LINK = ('https://ibqcjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/'
                'en/sites/CX_1/requisitions')
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
