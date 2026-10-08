"""
Job postings scraper for school_id 1682 - Sorbonne University (France)
ATS platform: own website
Careers link: https://jobs.sorbonne-universite.fr/homepage.aspx?LCID=2057

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Sorbonne University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Talentsoft board: the full list (list-of-all-jobs.aspx?all=1) links every
offer as /offre-de-emploi/emploi-<slug>_<id>.aspx (French form; the English
/job/job-<slug>_<id>.aspx is the same offer), deduplicated by id. The list
takes ~10 s to render.

Writes school_job_posts/school_id_1682_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1682_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1682
SCHOOL_NAME = 'Sorbonne University'
CAREERS_LINK = 'https://jobs.sorbonne-universite.fr/homepage.aspx?LCID=2057'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


FULL_LIST = 'https://jobs.sorbonne-universite.fr/job/list-of-all-jobs.aspx?all=1&mode=layer'
POSTING_RE = re.compile(r'^https://jobs\.sorbonne-universite\.fr/job/job-[^/?#]+_\d+\.aspx$', re.I)


FULL_LIST = 'https://jobs.sorbonne-universite.fr/job/list-of-all-jobs.aspx?all=1&mode=layer'
POSTING_RE = re.compile(r'^https://jobs\.sorbonne-universite\.fr/(?:offre-de-emploi/emploi|job/job)-[^/?#]+_\d+\.aspx$', re.I)


def find_links():
    html = lib._fetch_rendered_retry(FULL_LIST, 10000)
    by_id = {}
    for url in lib.extract_links(html, FULL_LIST):
        m = POSTING_RE.match(url)
        if m:
            by_id.setdefault(re.search(r'_(\d+)\.aspx$', url).group(1), url)
    return list(by_id.values())


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
