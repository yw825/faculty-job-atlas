"""
Job postings scraper for school_id 1539 - Herzing University-Kenosha (US)
ATS platform: UKG/Ultipro (detected: ultipro)
Careers link: https://recruiting2.ultipro.com/HER1009HRZ/JobBoard/267d2e37-abff-4559-8a18-a754503d3749

Herzing University-Kenosha runs on a shared ATS platform -- every school on ultipro uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_ultipro adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every ultipro school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 3 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Herzing University-Minneapolis, Herzing University-Brookfield.

Writes school_job_posts/school_id_1539_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1539_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1539
SCHOOL_NAME = 'Herzing University-Kenosha'
CAREERS_LINK = 'https://recruiting2.ultipro.com/HER1009HRZ/JobBoard/267d2e37-abff-4559-8a18-a754503d3749'
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
