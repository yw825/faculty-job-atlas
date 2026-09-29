"""
Job postings scraper for school_id 1907 - North Carolina Agricultural and Technical State University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.ncat.edu/postings/search

North Carolina A&T runs on a shared ATS platform -- every school on
peopleadmin uses the same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

This school was missing from schools_master entirely until 2026-09-29 -- it
was not a broken scraper but an absent one, found when a live posting
(jobs.ncat.edu/postings/41704, "Assistant/Associate Professor - Business
Information Systems") could not be located anywhere in the dataset.

Worth knowing: the adapter reads PeopleAdmin's ATOM feed, not the HTML
search page. That matters here -- the search page shows 30 postings while
the feed carries 132, so a scraper built on the visible page would have
silently collected less than a quarter of this school's jobs. Verified
before adding: the adapter returns 132 links and posting 41704 is among them.

Writes school_job_posts/school_id_1907_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1907_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1907
SCHOOL_NAME = 'North Carolina Agricultural and Technical State University'
CAREERS_LINK = 'https://jobs.ncat.edu/postings/search'
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
