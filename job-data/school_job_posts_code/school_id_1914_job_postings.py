"""
Job postings scraper for school_id 1914 - National College of Ireland (Ireland)
ATS platform: own website
Careers link: https://www.vacancies.ncirl.ie/jobs?source=ncirl.ie

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for National College of Ireland; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is www.vacancies.ncirl.ie/job/<slug>-<id> (stored without
?source=ncirl.ie). The "save_job" and "apply" links under each posting are
excluded by the pattern. The board is built client-side, so it is rendered.

Writes school_job_posts/school_id_1914_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1914_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1914
SCHOOL_NAME = 'National College of Ireland'
CAREERS_LINK = 'https://www.vacancies.ncirl.ie/jobs?source=ncirl.ie'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.vacancies\.ncirl\.ie/job/[a-z0-9-]+-\d+(?=$|\?)', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(CAREERS_LINK, POSTING_RE, render=True):
        url = POSTING_RE.match(url).group(0)      # drop ?source=ncirl.ie
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
