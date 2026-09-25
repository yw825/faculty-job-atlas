"""
Job postings scraper for school_id 1323 - The University of Tennessee-Chattanooga (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?lastSelectedFacet=LOCATIONS&mode=location&selectedLocationsFacet=300000010467888

The University of Tennessee-Chattanooga runs on a shared ATS platform -- every
school on oracle uses the same underlying site software, so this calls the
shared job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below and
pass it to run_checkpointed instead of editing the shared adapter.

The careers link was an fscmUI deeplink (objType=IRC_RECRUITING) that never
issued a job request, so the adapter timed out waiting for one.

The important part is what NOT to use instead. This host is the University of
Tennessee SYSTEM board: unfiltered it returns about 500 postings spread
across Knoxville, Memphis, Nashville, Tullahoma, Huntsville and Chattanooga,
and storing all of them here would credit the whole system's hiring to one
campus -- the same error that makes USC Aiken unusable, since that board
names no campus at all and so cannot be split.

This one can be split. The site exposes a LOCATIONS facet, and pinning
Chattanooga's id returns 36 postings, every one of them located in
Chattanooga ("Collections Specialist, Office of the Bursar - UT
Chattanooga"). UT-Martin's scraper uses the same mechanism with its own
facet id, which is why that school correctly holds 16 rather than 500.

Writes school_job_posts/school_id_1323_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1323_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1323
SCHOOL_NAME = 'The University of Tennessee-Chattanooga'
CAREERS_LINK = ('https://fa-ewlq-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/'
                'CandidateExperience/en/sites/CX_1/requisitions'
                '?lastSelectedFacet=LOCATIONS&mode=location'
                '&selectedLocationsFacet=300000010467888')
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
