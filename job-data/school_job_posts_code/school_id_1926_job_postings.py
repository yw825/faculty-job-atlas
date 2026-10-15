"""
Job postings scraper for school_id 1926 - University of Massachusetts-Chan Medical School (US)
ATS platform: AcademicJobsOnline
Careers link: https://academicjobsonline.org/ajo/UMASSMED

UMass Chan posts its faculty and postdoc openings on AcademicJobsOnline;
postings are academicjobsonline.org/ajo/jobs/<id>.

Writes school_job_posts/school_id_1926_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1926_job_postings.checkpoint next to this script.

TUNED FIND_LINKS

"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1926
SCHOOL_NAME = 'University of Massachusetts-Chan Medical School'
CAREERS_LINK = 'https://academicjobsonline.org/ajo/UMASSMED'
ATS_PLATFORM = 'AcademicJobsOnline'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [u for u in lib.scrape_academicjobsonline(CAREERS_LINK) if re.fullmatch(r'https://academicjobsonline\.org/ajo/jobs/\d+', u)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
