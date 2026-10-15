"""
Job postings scraper for school_id 1929 - University of Maine-School of Law (US)
ATS platform: Oracle Cloud HCM (UMS)
Careers link: https://fa-ewca-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?lastSelectedFacet=ORGANIZATIONS&selectedOrganizationsFacet=300000014113638

The University of Maine System shares one Oracle board; the link carries its
Organization filter for the School of Law, read through the REST service.

Writes school_job_posts/school_id_1929_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1929_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1929
SCHOOL_NAME = 'University of Maine-School of Law'
CAREERS_LINK = 'https://fa-ewca-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?lastSelectedFacet=ORGANIZATIONS&selectedOrganizationsFacet=300000014113638'
ATS_PLATFORM = 'Oracle Cloud HCM (UMS)'

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
