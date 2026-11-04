"""
Job postings scraper for school_id 72 - California State University-Bakersfield (US)
ATS platform: own website
Careers link: https://careers.csub.edu/en-us/filter/?search-keyword=&work-type=instructional%20faculty%20-%20temporary%2flecturer&work-type=instructional%20faculty%20%e2%80%93%20tenured%2ftenure-track&work-type=instructional%20student%20assistant&work-type=non-instructional%20faculty%20(coach%2fcounselor%2flibrarian)&work-type=teaching%20associate&job-mail-subscribe-privacy=agree

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for California State University-Bakersfield; nothing here affects any
other school's script.

Link check (ok): 23 posting-shaped links found -- rendered.

TUNED FIND_LINKS
This is a PageUp board. Postings are <board>/en-us/job/<id>/<slug>, read
only from the #search-results block; the "More Jobs" pager is followed to
the end (lib.scrape_pageup), because the first page shows just 20.

Writes school_job_posts/school_id_72_job_posts.csv (school_id, post_link).
Checkpointed to school_id_72_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 72
SCHOOL_NAME = 'California State University-Bakersfield'
CAREERS_LINK = 'https://careers.csub.edu/en-us/filter/?search-keyword=&work-type=instructional%20faculty%20-%20temporary%2flecturer&work-type=instructional%20faculty%20%e2%80%93%20tenured%2ftenure-track&work-type=instructional%20student%20assistant&work-type=non-instructional%20faculty%20(coach%2fcounselor%2flibrarian)&work-type=teaching%20associate&job-mail-subscribe-privacy=agree'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_pageup(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
