"""
Job postings scraper for school_id 1973 - The University of Texas M. D. Anderson Cancer Center (US)
ATS platform: own website
Careers link: https://jobs.mdanderson.org/careers/faculty

MD Anderson lists faculty openings as "Req #" sections on its clinical and research faculty pages (url #<slug>).

Writes school_job_posts/school_id_1973_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1973_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1973
SCHOOL_NAME = "The University of Texas M. D. Anderson Cancer Center"
CAREERS_LINK = 'https://jobs.mdanderson.org/careers/faculty'
ATS_PLATFORM = 'own website'

PAGES = ('https://www.mdanderson.org/about-md-anderson/careers/clinical-faculty-positions.html', 'https://www.mdanderson.org/about-md-anderson/careers/research-faculty-positions.html')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for page in PAGES:
        links += [f'{page}#{slug}' for slug, title, _b in lib.accordion_items(page, 'h4', render=True) if title.startswith('Req #')]
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
