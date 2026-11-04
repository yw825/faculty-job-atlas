"""
Job postings scraper for school_id 987 - Clarkson University (US)
ATS platform: iCIMS (detected: icims)
Careers link: https://careerhub-clarkson.icims.com

Clarkson University runs on a shared ATS platform -- every school on icims uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_icims adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every icims school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

Writes school_job_posts/school_id_987_job_posts.csv (school_id, post_link).
Checkpointed to school_id_987_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Clarkson's career hub links a separate iCIMS site for faculty, which is read.
Clarkson's career hub links a separate iCIMS site for faculty; its list is
read from the iCIMS frame address (?in_iframe=1).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 987
SCHOOL_NAME = 'Clarkson University'
CAREERS_LINK = 'https://careerhub-clarkson.icims.com'
ATS_PLATFORM = 'iCIMS'
PLATFORM = 'icims'

BOARD = 'https://faculty-clarkson.icims.com/jobs/search?ss=1&in_iframe=1'

POSTING_RE = re.compile(r'^https://faculty-clarkson\.icims\.com/jobs/\d+/[^/]+/job')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_matching(BOARD, POSTING_RE, render=False)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
