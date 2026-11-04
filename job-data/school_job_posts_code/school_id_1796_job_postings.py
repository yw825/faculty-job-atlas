"""
Job postings scraper for school_id 1796 - Griffith University (Australia)
ATS platform: SmartRecruiters (detected: smartrecruiters)
Careers link: https://jobs.smartrecruiters.com/GriffithUniversity/careers

Griffith's own careers page (griffith.edu.au/jobs/search-jobs) is actually
a front end for SmartRecruiters -- confirmed live via a network request to
subscriptions.smartrecruiters.com on page load, then confirming the real
company slug ("GriffithUniversity") against the public SmartRecruiters API
directly (48 real postings). Every school on smartrecruiters uses the same
shared job_postings_lib.scrape_smartrecruiters adapter rather than
duplicating platform-specific API logic here.

Writes school_job_posts/school_id_1796_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1796_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1796
SCHOOL_NAME = 'Griffith University'
CAREERS_LINK = 'https://jobs.smartrecruiters.com/GriffithUniversity/careers'
ATS_PLATFORM = 'SmartRecruiters'
PLATFORM = 'smartrecruiters'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK, CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
