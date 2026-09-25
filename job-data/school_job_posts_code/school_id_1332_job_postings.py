"""
Job postings scraper for school_id 1332 - Lincoln Memorial University (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://careers.lmunet.edu/

The careers link was https://www.peopleadmin.com/ -- the VENDOR's marketing
homepage rather than Lincoln Memorial's tenant, so the adapter asked
www.peopleadmin.com for an Atom feed and got a 404 on every run. The
university's own employment page links to careers.lmunet.edu, whose
/postings/all_jobs.atom answers with 146 entries.

Lincoln Memorial University runs on a shared ATS platform -- every school on peopleadmin uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every peopleadmin school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_1332_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1332_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1332
SCHOOL_NAME = 'Lincoln Memorial University'
CAREERS_LINK = 'https://careers.lmunet.edu/'
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
