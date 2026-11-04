"""
Job postings scraper for school_id 1741 - Universitat Politècnica de Catalunya (Spain)
ATS platform: own website
Careers link: https://treballa.upc.edu/ca/convocatories-de-concursos

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Universitat Politècnica de Catalunya; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1741_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1741_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
UPC's teaching and research staff (PDI) competitions are published on
treballa.upc.edu, one page per category (civil servant, permanent,
associate, temporary, Serra Hunter); each lists its calls as "Resolucio ..."
links followed by "ESTAT: OBERTA" while open. Only open calls are kept.
(The ReachMee example in the audit row belongs to the University of
Gothenburg -- same board id and key as Gothenburg's own link.)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1741
SCHOOL_NAME = 'Universitat Politècnica de Catalunya'
CAREERS_LINK = 'https://treballa.upc.edu/ca/convocatories-de-concursos'
ATS_PLATFORM = 'own website'

CATEGORY_PAGES = ('Concursos-pdi-funcionari', 'Concursos-pdi-laboral-permanent', 'concursos-professorat-associat',
                  'Concursos-pdi-laboral-temporal', 'Concursos-serra-hunter')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    links = []
    for page in CATEGORY_PAGES:
        status, html = lib.fetch_static(f'{CAREERS_LINK}/{page}', timeout=40)
        if status != 200:
            continue
        body = BeautifulSoup(html, 'html.parser').find(id='content') or BeautifulSoup(html, 'html.parser')
        calls = [a for a in body.find_all('a', href=True) if re.search(r'/resol', a['href']) and page.lower() in a['href'].lower()]
        text = body.get_text(' ', strip=True)
        for i, a in enumerate(calls):
            label = a.get_text(' ', strip=True)
            if not label.lower().startswith('resoluci'):
                continue
            start = text.find(label)
            nxt = next((text.find(b.get_text(' ', strip=True), start + len(label)) for b in calls[i + 1:]
                        if b.get_text(' ', strip=True).lower().startswith('resoluci')), -1)
            segment = text[start:nxt if nxt > start else start + 700]
            if re.search(r'ESTAT:\s*OBERTA', segment) and a['href'] not in links:
                links.append(a['href'])
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
