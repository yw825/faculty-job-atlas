"""
Job postings scraper for school_id 531 - Hampshire College (US)
ATS platform: ADP Workforce Now (detected: adp)
Careers link: https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=2723009e-ce54-4ba5-b0ed-f82b1e791964&ccId=19000101_000003&lang=en_US

Hampshire College runs on a shared ATS platform, so this calls the shared
job_postings_lib.scrape_adp adapter rather than duplicating platform-specific
logic here.

Hampshire embeds ADP into its own HR page as WEB COMPONENTS
(<recruitment-current-openings>, <recruitment-job-card>) rather than linking
out to a board or framing one, so there was no ADP URL anywhere to detect and
no anchors to scrape -- the page yielded exactly one link, itself. The
account id is carried as a cid attribute inside that page, which is where
the link above comes from.

Note the board answered with zero requisitions when this was written, so the
route is correct but unverified against real postings; Hampshire appears
simply not to be advertising anything right now, as with several other ADP
schools. It will collect normally once it does.

Writes school_job_posts/school_id_531_job_posts.csv (school_id, post_link).
Checkpointed to school_id_531_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 531
SCHOOL_NAME = 'Hampshire College'
CAREERS_LINK = ('https://workforcenow.adp.com/mascsr/default/mdf/recruitment/'
                'recruitment.html?cid=2723009e-ce54-4ba5-b0ed-f82b1e791964'
                '&ccId=19000101_000003&lang=en_US')
ATS_PLATFORM = 'ADP Workforce Now'
PLATFORM = 'adp'

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
