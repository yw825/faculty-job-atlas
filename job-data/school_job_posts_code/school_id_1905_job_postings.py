"""
Job postings scraper for school_id 1905 - emlyon business school (France)
ATS platform: Workday
Careers link: https://galileo.wd3.myworkdayjobs.com/emlyon_career_site

Uses the shared Workday adapter (job_postings_lib.scrape_workday).

The tenant `galileo` is the Galileo Global Education group, which owns
several schools -- so a group tenant would normally be a pooling risk, the
same trap that put one board's jobs under three schools elsewhere in this
set. It is safe here because the site path `emlyon_career_site` is already
emlyon's own: all 48 requisitions it returns are located in Lyon (45),
Paris (2) and one multi-location, i.e. emlyon's own campuses, with no other
Galileo school's postings mixed in. Verified before this school was added.

Worth knowing for later: at the time of writing this board carried zero
faculty postings -- all 48 are administrative and pedagogical-support roles
(coordinators, advisers, registry staff). That is a point-in-time fact
about emlyon's hiring, not a fault in this scraper; academic posts will be
collected the same way when emlyon lists them.

Writes school_job_posts/school_id_1905_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1905_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1905
SCHOOL_NAME = 'emlyon business school'
CAREERS_LINK = 'https://galileo.wd3.myworkdayjobs.com/emlyon_career_site'
ATS_PLATFORM = 'Workday'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_workday(CAREERS_LINK, school_name=SCHOOL_NAME)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
