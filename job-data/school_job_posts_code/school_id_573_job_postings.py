"""
Job postings scraper for school_id 573 - Western New England University (US)
ATS platform: Paycom (detected: paycom)
Careers link: https://www.paycomonline.net/v4/ats/web.php/jobs?clientkey=3C67A483237F6A324625AB95D568B0C1&fromClientSide=true

Western New England University runs on a shared ATS platform -- every school on paycom uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_paycom adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every paycom school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_573_job_posts.csv (school_id, post_link).
Checkpointed to school_id_573_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 573
SCHOOL_NAME = 'Western New England University'
CAREERS_LINK = 'https://www.paycomonline.net/v4/ats/web.php/jobs?clientkey=3C67A483237F6A324625AB95D568B0C1&fromClientSide=true'
ATS_PLATFORM = 'Paycom'
PLATFORM = 'paycom'

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
