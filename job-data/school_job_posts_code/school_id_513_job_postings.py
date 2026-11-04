"""
Job postings scraper for school_id 513 - Southeastern Louisiana University (US)
ATS platform: Workday (detected: workday)
Careers link: https://ulsselu.wd503.myworkdayjobs.com/SLU

Southeastern Louisiana University runs on a shared ATS platform, so this
calls the shared job_postings_lib.scrape_workday adapter rather than
duplicating platform-specific logic here.

This previously did a structural scrape of www.southeastern.edu/about/
employment, an HR information page that links out to the board rather than
listing anything, so it collected site navigation ("Skip to main content",
"Current Southeastern Employee Applicants", an employee testimonial).

The board is ulsselu.wd503.myworkdayjobs.com/SLU, which returns 21 postings
including "Department Head of Biological Sciences".

Worth noting the other Workday URL on that HR page, wd503.myworkday.com/
ulsselu/, is the INTERNAL tenant rather than the public job board -- it is
the one this file's header used to name, and it lists nothing publicly.

Writes school_job_posts/school_id_513_job_posts.csv (school_id, post_link).
Checkpointed to school_id_513_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 513
SCHOOL_NAME = 'Southeastern Louisiana University'
CAREERS_LINK = 'https://ulsselu.wd503.myworkdayjobs.com/SLU'
ATS_PLATFORM = 'Workday'
PLATFORM = 'workday'

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
