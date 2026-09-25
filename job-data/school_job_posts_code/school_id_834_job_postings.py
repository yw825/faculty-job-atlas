"""
Job postings scraper for school_id 834 - University of Nebraska at Kearney (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://unk.peopleadmin.com/

University of Nebraska at Kearney runs on a shared ATS platform, so this
calls the shared job_postings_lib.scrape_peopleadmin adapter rather than
duplicating platform-specific logic here.

The careers link was a NEWS ARTICLE -- unknews.unk.edu's story about endowed
faculty appointments -- so the scraper harvested that article's navigation
(a category link, a datestamp, a wp-login link) and never saw a job board at
all. UNK's board is unk.peopleadmin.com.

Note the system-wide careers.nebraska.edu board is deliberately NOT used
here: its feed answers with the single entry "No Positions Currently Open",
while UNK's own tenant carries the real posting.

Writes school_job_posts/school_id_834_job_posts.csv (school_id, post_link).
Checkpointed to school_id_834_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 834
SCHOOL_NAME = 'University of Nebraska at Kearney'
CAREERS_LINK = 'https://unk.peopleadmin.com/'
ATS_PLATFORM = 'PeopleAdmin'
PLATFORM = 'peopleadmin'

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
