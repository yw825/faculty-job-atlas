"""
Job postings scraper for school_id 1665 - Université catholique de Louvain (Belgium)
ATS platform: own website
Careers link: https://uclouvain.be/fr/emploi/listes-des-cours-vacants-par-faculte

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Université catholique de Louvain; nothing here affects any
other school's script.

TUNED FIND_LINKS
UCLouvain posts its vacant courses as one page per faculty/school/
institute (/fr/emploi/faculte-..., ecole-..., institut-..., louvain-...),
each listing that unit's vacant courses; each such page is one posting, as
in the example (faculte-de-theologie-et-detude-des-religions). The "-0"
pages are a second list for the same unit and are kept.

Writes school_job_posts/school_id_1665_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1665_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1665
SCHOOL_NAME = 'Université catholique de Louvain'
CAREERS_LINK = 'https://uclouvain.be/fr/emploi/listes-des-cours-vacants-par-faculte'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


FACULTY_PAGE_RE = re.compile(r'^https://uclouvain\.be/fr/emploi/(?:faculte|ecole|institut|louvain)[^/?#]*$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, FACULTY_PAGE_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
