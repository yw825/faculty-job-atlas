"""
Job postings scraper for school_id 32 - Henderson State University (US)
ATS platform: Taleo (detected: taleo)
Careers link: https://phe.tbe.taleo.net/phe02/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=48&org=ARKASTAT2

Henderson State University runs on a shared ATS platform -- every school on taleo uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_taleo adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every taleo school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_32_job_posts.csv (school_id, post_link).
Checkpointed to school_id_32_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 32
SCHOOL_NAME = 'Henderson State University'
CAREERS_LINK = 'https://phe.tbe.taleo.net/phe02/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=48&org=ARKASTAT2'
ATS_PLATFORM = 'Taleo'
PLATFORM = 'taleo'

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
