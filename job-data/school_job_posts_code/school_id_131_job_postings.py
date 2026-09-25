"""
Job postings scraper for school_id 131 - Northcentral University (US)
ATS platform: none -- institution is defunct
Careers link: none

THIS UNIVERSITY NO LONGER EXISTS. Northcentral University merged into
National University in autumn 2022, and National University is already a
separate row here (school 129, nus.wd1.myworkdayjobs.com). Pointing this
school at that board would simply duplicate 129's postings under a second
name, which is the multi-campus pooling fault being removed elsewhere in
this codebase.

What made this worth fixing rather than leaving: the careers link was
https://www.northcentral.edu/about/employment/current-job-openings/, and
northcentral.edu belongs to NORTH CENTRAL UNIVERSITY in Minneapolis -- a
different, still-operating institution which is school 679 here. So this
row was quietly republishing another university's vacancies under a defunct
school's name, and both schools held the identical 15 links.

find_links() therefore returns nothing. An empty list is the honest answer
for an institution that does no hiring, and run_checkpointed records it as
complete with zero links rather than as a permanent error.

Writes school_job_posts/school_id_131_job_posts.csv (school_id, post_link).
Checkpointed to school_id_131_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 131
SCHOOL_NAME = 'Northcentral University'
CAREERS_LINK = ''
ATS_PLATFORM = 'none (defunct institution)'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    """No board: the institution merged into National University (school 129)
    in 2022. Returning [] keeps this school empty instead of republishing
    North Central University's (school 679) postings under its name."""
    return []


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
