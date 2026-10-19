"""
Job postings scraper for school_id 1115 - George Fox University (US)
ATS platform: ApplicantPool (three separate boards)
Careers link: https://georgefoxfaculty.applicantpool.com/jobs/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

George Fox does not host its postings: its careers page is a landing page
whose "External Candidates" links lead to THREE separate ApplicantPool
boards -- faculty, staff and adjunct. Scraping the landing page collected
those three board links plus site navigation and no actual postings, so all
three boards are read here and their postings unioned.

Writes school_job_posts/school_id_1115_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1115_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
ApplicantPool faculty board.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1115
SCHOOL_NAME = 'George Fox University'
CAREERS_LINK = 'https://georgefoxfaculty.applicantpool.com/jobs/'
ATS_PLATFORM = 'ApplicantPool'

# Faculty and adjunct openings sit on two ApplicantPool boards (the staff board is left out).
BOARDS = ('https://georgefoxfaculty.applicantpool.com/jobs/',
          'https://georgefoxadjunct.applicantpool.com/jobs/')
POSTING_RE = re.compile(r'^https://georgefox(?:faculty|adjunct)\.applicantpool\.com/jobs/\d+$')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for board in BOARDS:
        links += [u for u in lib.scrape_matching(board, POSTING_RE, render=True, wait_ms=6000) if u not in links]
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
