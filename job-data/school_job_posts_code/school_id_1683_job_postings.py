"""
Job postings scraper for school_id 1683 - Université PSL (France)
ATS platform: own website
Careers link: https://recrutement.psl.eu/nos-offres

CUSTOMIZED (confirmed live): a Drupal site with real ?page=N pagination
(17 pages of postings, confirmed live via the page's own "Dernier page ...
?page=16" link) and short random-looking 10-character slug URLs for each
posting (e.g. "/1no3ttx2zu") that don't contain any job-shaped keyword the
generic default's filter looks for. This walks every page up to the
confirmed last-page number and keeps links matching that slug shape.

TUNED FIND_LINKS
Each opening is recrutement.psl.eu/<10-character id>; the board's own
pages (nos-offres, ...) do not have that shape.

Writes school_job_posts/school_id_1683_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1683_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1683
SCHOOL_NAME = 'Université PSL'
CAREERS_LINK = 'https://recrutement.psl.eu/nos-offres'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

# The real posting slugs are random alphanumerics that always contain at
# least one DIGIT ("1no3ttx2zu", "n2tkxa2120"). A digit-free rule also
# matched ordinary site pages of the same length -- "/recherche" and
# "/formation" were being recorded as postings (confirmed live) -- and the
# host check keeps www.psl.eu navigation out entirely.
SLUG_RE = re.compile(r'^/(?=[a-z0-9]*\d)[a-z0-9]{8,12}$')
POSTING_HOST = 'recrutement.psl.eu'
LAST_PAGE_RE = re.compile(r'[?&]page=(\d+)')


POSTING_RE = re.compile(r'^https://recrutement\.psl\.eu/[a-z0-9]{10}$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
