"""
Job postings scraper for school_id 1874 - Northumbria University (United Kingdom)
ATS platform: Oracle Cloud HCM (detected: oracle)
Careers link: https://work4.northumbria.ac.uk/#en/sites/CX_1001/jobs

Northumbria runs Oracle Cloud HCM on a white-labeled custom domain
(work4.northumbria.ac.uk), not the usual *.oraclecloud.com host --
job_postings_lib.detect_platform() didn't recognize it as Oracle until
extended to also match the "/hcmUI/CandidateExperience/.../sites/<id>/jobs"
URL signature regardless of hostname. Confirmed live: 12 real postings via
the same shared job_postings_lib.scrape_oracle adapter every other Oracle
school uses, matching exactly.

Writes school_job_posts/school_id_1874_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1874_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1874
SCHOOL_NAME = 'Northumbria University'
CAREERS_LINK = 'https://work4.northumbria.ac.uk/#en/sites/CX_1001/jobs'
ATS_PLATFORM = 'Oracle Cloud HCM'
PLATFORM = 'oracle'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK, CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
