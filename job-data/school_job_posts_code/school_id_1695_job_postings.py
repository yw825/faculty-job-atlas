"""
Job postings scraper for school_id 1695 - National Technical University of Athens (Greece)
ATS platform: APELLA (Greece) (detected: apella)
Careers link: https://apella.minedu.gov.gr/en/positions

National Technical University of Athens runs on a shared ATS platform -- every school on apella uses the
exact same underlying site software, so this calls the shared
job_postings_lib.scrape_apella adapter rather than duplicating
platform-specific API logic here. If results for this ONE school still need
a tweak that shouldn't apply to every apella school, override find_links
below instead of editing the shared adapter.

Writes school_job_posts/school_id_1695_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1695_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1695
SCHOOL_NAME = 'National Technical University of Athens'
CAREERS_LINK = 'https://apella.minedu.gov.gr/en/positions'
ATS_PLATFORM = 'APELLA (Greece)'
PLATFORM = 'apella'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK, CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
