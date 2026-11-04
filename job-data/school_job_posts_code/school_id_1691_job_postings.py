"""
Job postings scraper for school_id 1691 - University of Mannheim (Germany)
ATS platform: own website
Careers link: https://www.uni-mannheim.de/en/about/working-at-the-university/job-vacancies/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Mannheim; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is a PDF under /media/.../Ausschreibungen_Stellenanzeigen/
(stored without the "/flipbook" viewer suffix the page sometimes adds).
The vacancy list is built client-side, so the page is rendered.

Writes school_job_posts/school_id_1691_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1691_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1691
SCHOOL_NAME = 'University of Mannheim'
CAREERS_LINK = 'https://www.uni-mannheim.de/en/about/working-at-the-university/job-vacancies/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.uni-mannheim\.de/media/Universitaet/Dokumente/Ausschreibungen_Stellenanzeigen/[^/?#]+\.pdf', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True):
        url = POSTING_RE.match(url).group(0)      # drop the /flipbook viewer suffix
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
