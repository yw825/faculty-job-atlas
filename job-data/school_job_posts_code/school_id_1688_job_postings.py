"""
Job postings scraper for school_id 1688 - Goethe University Frankfurt (Germany)
ATS platform: own website
Careers link: https://berufungsportal.uni-frankfurt.de/

CUSTOMIZED (confirmed live): this is a Vaadin single-page app (the
university's professorship appointment portal) that needs noticeably longer
than the generic default's 2-second render wait before "Available
Positions" actually appears -- confirmed live, a 2s wait showed only the
word "Online" (the page's own status widget), a 5s wait showed both real
postings. Each posting has an "Apply for this position" link
("application?procedure=<GUID>"), which doesn't contain any job-shaped
keyword the generic default's filter looks for; the parallel "Job Posting"
PDF link works too but the application link is the more stable identifier.

Writes school_job_posts/school_id_1688_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1688_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1688
SCHOOL_NAME = 'Goethe University Frankfurt'
CAREERS_LINK = 'https://berufungsportal.uni-frankfurt.de/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

APPLICATION_RE = re.compile(r'application\?procedure=')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK, href_pattern=APPLICATION_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
