"""
Job postings scraper for school_id 1743 - Universitat de Barcelona (Spain)
ATS platform: own website
Careers link: https://seu.ub.edu/ofertaPublicaCategoriaPublic/categories

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Universitat de Barcelona; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1743_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1743_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to UB's e-office list of public job
calls: 10 per page (offset=0,10,...), newest first, each call linked twice
(title and status). Calls whose status is "Oberta" (open) among the 50 newest are kept
(older calls keep that status forever); a call is
listPublicacionsAmbCategoria?categoria.id=<n>, the form of the audit's example.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1743
SCHOOL_NAME = 'Universitat de Barcelona'
CAREERS_LINK = 'https://seu.ub.edu/ofertaPublicaCategoriaPublic/categories'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def open_calls():
    """[(call url, title)] for every call marked Oberta."""
    from bs4 import BeautifulSoup
    out = []
    # Old calls are never marked closed (hundreds stay "Oberta" back to 2020),
    # so only the 50 newest calls are considered.
    for offset in range(0, 50, 10):
        status, html = lib.fetch_static(f'{CAREERS_LINK}?tipus=totes&max=10&offset={offset}', timeout=40)
        if status != 200:
            if offset == 0:
                raise RuntimeError(f'calls list status={status}')
            break
        titles, states = {}, {}
        for a in BeautifulSoup(html, 'html.parser').find_all('a', href=re.compile(r'categoria\.id=\d+')):
            cid = re.search(r'categoria\.id=(\d+)', a['href']).group(1)
            text = re.sub(r'\s+', ' ', a.get_text(' ', strip=True))
            if text.lower() in ('oberta', 'tancada', 'resolta', 'en curs', 'pendent', 'anul·lada'):
                states[cid] = text.lower()
            elif text:
                titles.setdefault(cid, text)
        if not titles:
            break
        fresh = [(f'https://seu.ub.edu/ofertaPublicaCategoriaPublic/listPublicacionsAmbCategoria?categoria.id={cid}', t)
                 for cid, t in titles.items() if states.get(cid) == 'oberta']
        if not fresh and offset >= 20:
            break
        out += [x for x in fresh if x not in out]
    return out


def find_links():
    return [url for url, _title in open_calls()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
