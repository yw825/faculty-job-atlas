"""
Job postings scraper for school_id 1730 - University of Warsaw (Poland)
ATS platform: Poland national portal (detected: poland_nauka)
Careers link: https://bazaogloszen.nauka.gov.pl/wyniki-wyszukiwania/

University of Warsaw runs on a shared ATS platform -- every school on poland_nauka uses the
exact same underlying site software, so this calls the shared
job_postings_lib.scrape_poland_nauka adapter rather than duplicating
platform-specific API logic here. If results for this ONE school still need
a tweak that shouldn't apply to every poland_nauka school, override find_links
below instead of editing the shared adapter.

Writes school_job_posts/school_id_1730_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1730_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1730
SCHOOL_NAME = 'University of Warsaw'
CAREERS_LINK = 'https://bazaogloszen.nauka.gov.pl/wyniki-wyszukiwania/'
ATS_PLATFORM = 'Poland national portal'
PLATFORM = 'poland_nauka'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK, CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
