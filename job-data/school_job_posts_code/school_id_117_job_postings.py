"""
Job postings scraper for school_id 117 - Simpson University (US)
ATS platform: UKG Ready "TA" career site (detected: ultipro_ta)
Careers link: https://secure.onehcm.com/ta/Simpson.careers?CareersSearch&InFrameset=1&HostedBy=simpsonu.edu

Simpson University runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_ultipro_ta adapter rather than duplicating
platform-specific logic here.

This previously did a generic rendered-page scrape, which cannot work on
this board: the listing is built by JS and the served HTML is a ~32KB shell
whose only hrefs are three stylesheets, so the school recorded one
navigation link and no postings. The board's own public XHR lists the
requisitions (32 for Simpson), and Simpson.careers?ShowJob=<id> renders each
one for a human.

If results for THIS ONE school need a tweak that shouldn't apply to every
ultipro_ta school, define find_links() below and pass it to run_checkpointed
instead of editing the shared adapter.

Writes school_job_posts/school_id_117_job_posts.csv (school_id, post_link).
Checkpointed to school_id_117_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 117
SCHOOL_NAME = 'Simpson University'
CAREERS_LINK = 'https://secure.onehcm.com/ta/Simpson.careers?CareersSearch&InFrameset=1&HostedBy=simpsonu.edu'
ATS_PLATFORM = 'UKG Ready (TA career site)'
PLATFORM = 'ultipro_ta'

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
