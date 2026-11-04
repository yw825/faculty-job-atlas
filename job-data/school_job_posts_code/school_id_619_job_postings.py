"""
Job postings scraper for school_id 619 - University of Maine-Orono (US)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://fa-ewca-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?lastSelectedFacet=ORGANIZATIONS&selectedOrganizationsFacet=300000014113612

University of Maine runs on a shared ATS platform -- every school on oracle uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_oracle adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every oracle school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_619_job_posts.csv (school_id, post_link).
Checkpointed to school_id_619_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The University of Maine System shares one Oracle board; the link carries its
Organization filter for this campus, read through the board's REST service.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 619
SCHOOL_NAME = 'University of Maine-Orono'
CAREERS_LINK = 'https://fa-ewca-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?lastSelectedFacet=ORGANIZATIONS&selectedOrganizationsFacet=300000014113612'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_oracle_link(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
