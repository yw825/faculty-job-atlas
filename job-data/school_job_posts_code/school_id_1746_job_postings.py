"""
Job postings scraper for school_id 1746 - Universidad Complutense de Madrid (Spain)
ATS platform: own website
Careers link: https://www.ucm.es/empleo-ucm

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Universidad Complutense de Madrid; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1746_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1746_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The audit points to the "Calls for Applications for Teaching and Research
Staff (PDI)" section: it links one page per staff category (civil-servant
chairs, permanent lecturer, assistant professor, ...), and each of those
lists its calls as links dated in the text ("Convocatoria publicada en el
BOUC de 15 de septiembre de 2026", "... (BOE de 31 de agosto de 2026)").
Calls dated within the last 60 days are kept; the lists go back years.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1746
SCHOOL_NAME = 'Universidad Complutense de Madrid'
CAREERS_LINK = 'https://www.ucm.es/empleo-ucm'
ATS_PLATFORM = 'own website'

CATEGORY_PAGES = ('funcionarios-de-carrera-2', 'profesor-a-permanente-laboral', 'profesor-asociado',
                  'profesor-asociado-de-ciencias-de-la-salud', 'profesor-ayudante-doctor', 'profesor-sustituto')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    import datetime
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    months = {m: i + 1 for i, m in enumerate(['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                                              'septiembre', 'octubre', 'noviembre', 'diciembre'])}
    today = datetime.date.today()
    links = []
    for path in CATEGORY_PAGES:
        status, html = lib.fetch_static('https://www.ucm.es/' + path, timeout=40)
        if status != 200:
            continue
        for a in BeautifulSoup(html, 'html.parser').find_all('a', href=True):
            text = re.sub(r'\s+', ' ', a.get_text(' ', strip=True))
            m = re.search(r'(\d{1,2}) de ([a-záéíóú]+) de (\d{4})', text.lower())
            if not m or m.group(2) not in months or not re.search(r'(?i)convocatoria|concurso', text):
                continue
            try:
                when = datetime.date(int(m.group(3)), months[m.group(2)], int(m.group(1)))
            except ValueError:
                continue
            url = urljoin('https://www.ucm.es/', a['href'])
            if 0 <= (today - when).days <= 60 and url not in links:
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
