"""
Job postings scraper for school_id 1681 - Sciences Po (France)
ATS platform: own website
Careers link: https://www.sciencespo.fr/travailler-a-sciencespo/nos-offres/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Sciences Po; nothing here affects any
other school's script.

TUNED FIND_LINKS
Sciences Po's page links its Talentsoft board; the board's full list
(liste-toutes-offres.aspx?all=1) holds every offer ("28 offres" on
2026-10-08), each /offre-de-emploi/emploi-<slug>_<id>.aspx.

Writes school_job_posts/school_id_1681_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1681_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1681
SCHOOL_NAME = 'Sciences Po'
CAREERS_LINK = 'https://www.sciencespo.fr/travailler-a-sciencespo/nos-offres/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


LISTING = 'https://sciencespo-career.talent-soft.com/offre-de-emploi/liste-toutes-offres.aspx?all=1&mode=layer'
POSTING_RE = re.compile(r'^https://sciencespo-career\.talent-soft\.com/offre-de-emploi/emploi-[^/?#]+_\d+\.aspx$', re.I)


def find_links():
    return lib.scrape_matching(LISTING, POSTING_RE, render=True)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
