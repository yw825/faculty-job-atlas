"""
Job postings scraper for school_id 1685 - Free University of Berlin (Germany)
ATS platform: own website
Careers link: https://www.fu-berlin.de/universitaet/beruf-karriere/jobs/english/index.html

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Free University of Berlin; nothing here affects any
other school's script.

TUNED FIND_LINKS
The English jobs page only links a few category invitations; the
openings themselves are on FU's SuccessFactors board (jobs.fu-berlin.de,
/job/<slug>/<id>/), whose full search is walked page by page.

Writes school_job_posts/school_id_1685_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1685_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1685
SCHOOL_NAME = 'Free University of Berlin'
CAREERS_LINK = 'https://www.fu-berlin.de/universitaet/beruf-karriere/jobs/english/index.html'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


SEARCH = 'https://jobs.fu-berlin.de/search/?q=&locale=en_US'


def find_links():
    return lib.scrape_successfactors(SEARCH)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
