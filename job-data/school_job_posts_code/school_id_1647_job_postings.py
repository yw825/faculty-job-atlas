"""
Job postings scraper for school_id 1647 - Université Laval (Canada)
ATS platform: own website
Careers link: https://www.rh.ulaval.ca/emplois-disponibles/personnel-enseignant-et-de-recherche

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Université Laval; nothing here affects any
other school's script.

TUNED FIND_LINKS
The teaching-and-research page links one page per category (course
lecturers, medicine lecturers, research professionals, postdocs); those
pages link the postings on psk.rh.ulaval.ca. The audit noted "0 post", and
on 2026-10-08 the course-lecturer list (psk.rh.ulaval.ca/publique/
liste-pecc) rendered empty, so no posting shape has been confirmed yet; the
category pages themselves are deliberately not stored.

Writes school_job_posts/school_id_1647_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1647_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1647
SCHOOL_NAME = 'Université Laval'
CAREERS_LINK = 'https://www.rh.ulaval.ca/emplois-disponibles/personnel-enseignant-et-de-recherche'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


CATEGORY_RE = re.compile(r'^https://www\.rh\.ulaval\.ca/emplois-disponibles/personnel-enseignant-et-de-recherche/[^/?#]+$', re.I)
POSTING_RE = re.compile(r'^https://psk\.rh\.ulaval\.ca/publique/(?!liste-)[^?#]+$', re.I)


def find_links():
    return lib.scrape_two_hop(CAREERS_LINK, CATEGORY_RE, POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
