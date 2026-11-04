"""
Job postings scraper for school_id 1931 - Washington University in St Louis-Medical Campus (US)
ATS platform: own website
Careers link: https://facultyopportunities.wustl.edu/

WashU Medicine's faculty-opportunities portal (facultyopportunities.wustl.edu)
lists every School of Medicine faculty opening as /Posting/Detail/<id>. The
site answers plain requests with a Cloudflare check, so it is read in a
normal Chrome window.

Writes school_job_posts/school_id_1931_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1931_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1931
SCHOOL_NAME = 'Washington University in St Louis-Medical Campus'
CAREERS_LINK = 'https://facultyopportunities.wustl.edu/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_real_chrome(CAREERS_LINK, wait_ms=12000)
    html = html[1] if isinstance(html, tuple) else html
    links = [lib.urljoin(CAREERS_LINK, h) for h in re.findall(r'href="([^"]*?/Posting/Detail/\d+)"', html or '')]
    if not links:
        raise RuntimeError('faculty portal listed no postings')
    return list(dict.fromkeys(links))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
