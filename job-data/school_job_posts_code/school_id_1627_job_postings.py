"""
Job postings scraper for school_id 1627 - Algoma University (Canada)
ATS platform: own website
Careers link: https://algomau.ca/careers/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Algoma University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Faculty openings are Google Drive files (drive.google.com/file/d/<id>/view,
stored without ?usp=sharing); staff openings are "External-Job-Posting" PDFs
under /wp-content/uploads/. The Drive links only appear once the page is
rendered. Other uploads (e.g. the Academic Plan PDF) are excluded.

Writes school_job_posts/school_id_1627_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1627_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1627
SCHOOL_NAME = 'Algoma University'
CAREERS_LINK = 'https://algomau.ca/careers/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^(?:https://drive\.google\.com/file/d/[\w-]+'
                        r'|https://algomau\.ca/wp-content/uploads/\d{4}/\d{2}/[^?#]*Job-Posting[^?#]*\.pdf$)', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True):
        url = POSTING_RE.match(url).group(0)
        if url.startswith('https://drive.google.com/'):
            url += '/view'
        if url not in links:
            links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
