"""
Job postings scraper for school_id 931 - St Lawrence University (US)
ATS platform: iCIMS (detected: icims)
Careers link: https://careerhub-clarkson.icims.com/jobs/search?hashed=-625885781&mobile=false&width=1246&height=500&bga=true&needsRedirect=false&jan1offset=-300&jun1offset=-240

St Lawrence University runs on a shared ATS platform -- every school on icims uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_icims adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every icims school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_931_job_posts.csv (school_id, post_link).
Checkpointed to school_id_931_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 931
SCHOOL_NAME = 'St Lawrence University'
CAREERS_LINK = 'https://careerhub-clarkson.icims.com/jobs/search?hashed=-625885781&mobile=false&width=1246&height=500&bga=true&needsRedirect=false&jan1offset=-300&jun1offset=-240'
ATS_PLATFORM = 'iCIMS'
PLATFORM = 'icims'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
