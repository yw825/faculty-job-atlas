"""
Job postings scraper for school_id 1115 - George Fox University (US)
ATS platform: ApplicantPool (three separate boards)
Careers link: https://www.georgefox.edu/offices/hr/careers/index.html

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

George Fox does not host its postings: its careers page is a landing page
whose "External Candidates" links lead to THREE separate ApplicantPool
boards -- faculty, staff and adjunct. Scraping the landing page collected
those three board links plus site navigation and no actual postings, so all
three boards are read here and their postings unioned.

Writes school_job_posts/school_id_1115_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1115_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1115
SCHOOL_NAME = 'George Fox University'
CAREERS_LINK = 'https://www.georgefox.edu/offices/hr/careers/index.html'
ATS_PLATFORM = 'ApplicantPool'

BOARDS = ['https://georgefoxfaculty.applicantpool.com/jobs/',
          'https://georgefoxstaff.applicantpool.com/jobs/',
          'https://georgefoxadjunct.applicantpool.com/jobs/']
POSTING = re.compile(r'https://georgefox[a-z]*\.applicantpool\.com/jobs/\d+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links, seen, failures = [], set(), []
    for board in BOARDS:
        html = lib.fetch_rendered(board, wait_ms=8000)
        if lib.is_fetch_failure(html):
            failures.append(f'{board}: {html[:60]}')
            continue
        for u in sorted(set(POSTING.findall(html))):
            if u not in seen:
                seen.add(u)
                links.append(u)
    if not links:
        raise RuntimeError('no postings on any george fox board; '
                           + ' | '.join(failures))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
