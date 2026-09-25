"""
Job postings scraper for school_id 873 - Fairleigh Dickinson University-Florham Campus (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.fdu.edu/

Fairleigh Dickinson University-Florham Campus runs on a shared ATS platform,
so this calls the shared job_postings_lib.scrape_peopleadmin adapter rather
than duplicating platform-specific logic here.

The careers link was https://www.instagram.com/reel/Db53N_YDMHp/ -- an
INSTAGRAM REEL. Both FDU campuses pointed at it and both held zero postings.
FDU's board is jobs.fdu.edu, a PeopleAdmin tenant whose feed lists 51.

NOTE: 2 schools list against this same URL, so this listing carries every one
of their postings, not just this school's: Fairleigh Dickinson
University-Metropolitan Campus.

That pooling is deliberate here rather than an oversight. Rutgers' three
campuses were separated because its feed carries a <school> field naming the
chancellor's unit, which is exact. FDU's feed carries only the standard Atom
fields, and the campus is mentioned -- when it is mentioned at all -- in free
text: of the 51 entries, 24 name Florham, 4 name Metropolitan, 3 name
Vancouver, 3 name more than one, and 23 name no campus whatsoever. Splitting
on that would mean guessing the owner of 23 real jobs, so both campuses show
the whole board instead. Fifty-one real postings duplicated across two
campuses beats zero postings, and beats a confident wrong answer.

Writes school_job_posts/school_id_873_job_posts.csv (school_id, post_link).
Checkpointed to school_id_873_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 873
SCHOOL_NAME = 'Fairleigh Dickinson University-Florham Campus'
CAREERS_LINK = 'https://jobs.fdu.edu/'
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
