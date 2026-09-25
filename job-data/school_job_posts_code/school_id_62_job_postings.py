"""
Job postings scraper for school_id 62 - Arizona State University Digital Immersion
ATS platform: Interfolio
Careers link: https://apply.interfolio.com/9635/positions

ASU's own faculty site (facultypositions.asu.edu) renders only a subset of
its openings -- paging it to exhaustion yielded 25 of a claimed 500, and the
Department of Information Systems assistant professorship was never among
them. ASU's Interfolio board carries all 205, that one included.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 62
SCHOOL_NAME = 'Arizona State University Digital Immersion'
CAREERS_LINK = 'https://apply.interfolio.com/9635/positions'
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
