"""
Job postings scraper for school_id 1971 - The University of Texas Health Science Center at Houston (US)
ATS platform: Taleo
Careers link: https://careers.uth.tmc.edu/us/en/c/faculty-physicians-jobs

UTHealth Houston's Faculty & Physicians category (Phenom), 10 per page (?from=N).

Writes school_job_posts/school_id_1971_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1971_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1971
SCHOOL_NAME = "The University of Texas Health Science Center at Houston"
CAREERS_LINK = 'https://careers.uth.tmc.edu/us/en/c/faculty-physicians-jobs'
ATS_PLATFORM = 'Taleo'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for start in range(0, 600, 10):
        html = lib._fetch_rendered_retry(f'https://careers.uth.tmc.edu/us/en/c/faculty-physicians-jobs?from={start}&s=1', 6000)
        fresh = [u for u in dict.fromkeys(re.findall(r'https://careers\.uth\.tmc\.edu/us/en/job/[0-9A-Z]+/[^"\s<>]+', html)) if u not in links]
        if not fresh:
            break
        links += fresh
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
