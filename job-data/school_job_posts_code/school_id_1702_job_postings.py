"""
Job postings scraper for school_id 1702 - University College Cork (Ireland)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://ucc.peopleadmin.com/

University College Cork runs on a shared ATS platform, so this calls the
shared job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here.

The careers link was UCC's CoreHR board,
my.corehr.com/pls/uccrecruit/erq_search_version_4.start_search_with_params,
which answers every request with HTTP 403 -- as does every other CoreHR
tenant tried, including Oxford's. That made the school look permanently
unscrapable. It is not: UCC also runs a PeopleAdmin tenant at
ucc.peopleadmin.com whose Atom feed lists 116 postings.

Worth noting the CoreHR 403 is real and still unsolved -- Dublin City
University and University of Galway have no equivalent PeopleAdmin tenant
(every candidate hostname fails to resolve), so they remain unreachable.
A dead vendor board does not mean the university has no other board.

Writes school_job_posts/school_id_1702_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1702_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1702
SCHOOL_NAME = 'University College Cork'
CAREERS_LINK = 'https://ucc.peopleadmin.com/'
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
