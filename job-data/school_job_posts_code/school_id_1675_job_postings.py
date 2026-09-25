"""
Job postings scraper for school_id 1675 - INSEAD
ATS platform: Interfolio
Careers link: https://apply.interfolio.com/46334/positions

The Oracle Cloud candidate portal returned 20 links, none of them faculty
postings. INSEAD's faculty openings are on Interfolio board 46334.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1675
SCHOOL_NAME = 'INSEAD'
CAREERS_LINK = 'https://apply.interfolio.com/46334/positions'
ATS_PLATFORM = 'Interfolio'
PLATFORM = 'interfolio'

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
