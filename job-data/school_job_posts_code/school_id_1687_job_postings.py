"""
Job postings scraper for school_id 1687 - University of Cologne (Germany)
ATS platform: own website
Careers link: https://jobportal.uni-koeln.de/?offset=0&showFilter=false&tab=&sort=bewerbungsfrist&name=dynamisch&beschaeftigungArtFilter=WISS&beschaeftigungArtZusFilter=&titelFilter=

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Cologne; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is its flyer, /ausschreibung/renderFile/<id>?propertyName=flyer.
The portal lists 10 at a time (offset=0, 10, ...) and builds the list
client-side, so pages are rendered and walked until one adds nothing.

Writes school_job_posts/school_id_1687_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1687_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1687
SCHOOL_NAME = 'University of Cologne'
CAREERS_LINK = 'https://jobportal.uni-koeln.de/?offset=0&showFilter=false&tab=&sort=bewerbungsfrist&name=dynamisch&beschaeftigungArtFilter=WISS&beschaeftigungArtZusFilter=&titelFilter='
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://jobportal\.uni-koeln\.de/ausschreibung/renderFile/\d+\?propertyName=flyer$', re.I)


def find_links():
    links = []
    for page in range(30):
        url = re.sub(r'offset=\d+', f'offset={page * 10}', CAREERS_LINK)
        fresh = [u for u in lib.scrape_matching(url, POSTING_RE, render=True) if u not in links]
        if not fresh:
            break
        links.extend(fresh)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
