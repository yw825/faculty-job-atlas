"""
Job postings scraper for school_id 697 - University of St Thomas (US)
ATS platform: iCIMS (detected: icims)
Careers link: https://facultyemployment-stthomas.icims.com/jobs/intro?hashed=-435746366&mobile=false&width=1132&height=500&bga=true&needsRedirect=false&jan1offset=-480&jun1offset=-420

University of St Thomas runs on a shared ATS platform -- every school on icims uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_icims adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every icims school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_697_job_posts.csv (school_id, post_link).
Checkpointed to school_id_697_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to St. Thomas's faculty iCIMS site
(staff jobs are on a separate site).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 697
SCHOOL_NAME = 'University of St Thomas'
CAREERS_LINK = 'https://facultyemployment-stthomas.icims.com/jobs/intro?hashed=-435746366&mobile=false&width=1132&height=500&bga=true&needsRedirect=false&jan1offset=-480&jun1offset=-420'
ATS_PLATFORM = 'iCIMS'
PLATFORM = 'icims'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_icims(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
