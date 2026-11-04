"""
Job postings scraper for school_id 1661 - Université Libre de Bruxelles (Belgium)
ATS platform: own website
Careers link: https://www.ulb.be/fr/travailler-et-collaborer/vacances-d-emplois-academiques-et-scientifiques

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Université Libre de Bruxelles; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each faculty page (e.g. the Solvay page) lists its vacancies as "Lire
l'annonce" links to cwfront.ulb.ac.be -- vacacad/vacancies/download/<id>
or greffe/.../pdf/prod/<id>.pdf. The "liste complete" page carries every
faculty's vacancies at once, so it is read instead of each faculty page.

Writes school_job_posts/school_id_1661_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1661_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1661
SCHOOL_NAME = 'Université Libre de Bruxelles'
CAREERS_LINK = 'https://www.ulb.be/fr/travailler-et-collaborer/vacances-d-emplois-academiques-et-scientifiques'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


FULL_LIST = ('https://www.ulb.be/fr/vacances-d-emplois-academiques-et-scientifiques/'
             'liste-complete-des-vacances-academiques-et-scientifiques')
POSTING_RE = re.compile(r'^https://cwfront\.ulb\.ac\.be/(?:vacacad/vacancies/download/\d+'
                        r'|greffe/modules/vac/data/sources/pdf/prod/\d+\.pdf)$', re.I)


def find_links():
    return lib.scrape_matching(FULL_LIST, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
