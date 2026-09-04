"""
Job postings scraper for school_id 118 - University of Redlands (US)
ATS platform: UKG/Ultipro (detected: ultipro)
Careers link: https://recruiting2.ultipro.com/UNI1089UOR/JobBoard/6af23b67-9dd3-4a6a-bda1-676b92a4fcb4/?q=&o=postedDateDesc&w=&wc=&we=&wpst=&f5=2751WKaSbU2nBtQmI-bCAA

University of Redlands runs on a shared ATS platform -- every school on ultipro uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_ultipro adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every ultipro school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_118_job_posts.csv (school_id, post_link).
Checkpointed to school_id_118_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 118
SCHOOL_NAME = 'University of Redlands'
CAREERS_LINK = 'https://recruiting2.ultipro.com/UNI1089UOR/JobBoard/6af23b67-9dd3-4a6a-bda1-676b92a4fcb4/?q=&o=postedDateDesc&w=&wc=&we=&wpst=&f5=2751WKaSbU2nBtQmI-bCAA'
ATS_PLATFORM = 'UKG/Ultipro'
PLATFORM = 'ultipro'

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
