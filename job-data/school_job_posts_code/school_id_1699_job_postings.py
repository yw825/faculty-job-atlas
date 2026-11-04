"""
Job postings scraper for school_id 1699 - Eötvös Loránd University (Hungary)
ATS platform: own website
Careers link: https://www.elte.hu/allaspalyazatok

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Eötvös Loránd University; nothing here affects any
other school's script.

TUNED FIND_LINKS
ELTE's current calls are on Álláspályazatok (/allaspalyazatok): a table of
position, unit, open and close dates, each linking its call as a PDF in the
document store (/dstore/document/<id>/<name>.pdf). The six application
forms and privacy notices on the same page are dstore documents too and are
excluded by name. (The audited link, /en/work-opportunities, is a page from
May 2022 whose only PDF has since been deleted.)

Writes school_job_posts/school_id_1699_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1699_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1699
SCHOOL_NAME = 'Eötvös Loránd University'
CAREERS_LINK = 'https://www.elte.hu/allaspalyazatok'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://(?:www\.)?elte\.hu/(?:en/)?dstore/document/\d+/[^?#]+\.pdf', re.I)
NOT_A_POSTING_RE = re.compile(r'guide|summer|brochure|handbook', re.I)


DOC_RE = re.compile(r'(?:^https://(?:www\.)?elte\.hu)?/(?:en/)?dstore/document/\d+/', re.I)
# the page also links the application paperwork as dstore documents
FORM_RE = re.compile(r'nyilatkozat|permission|privacy|adatkezel', re.I)


# Hungarian academic ranks -> English, so titles classify and search like
# every other school's
RANKS = [('egyetemi tanár', 'Full Professor'), ('egyetemi docens', 'Associate Professor'),
         ('egyetemi adjunktus', 'Assistant Professor'), ('adjunktus', 'Assistant Professor'),
         ('egyetemi tanársegéd', 'Assistant Lecturer'), ('tanársegéd', 'Assistant Lecturer'),
         ('tudományos főmunkatárs', 'Senior Research Fellow'), ('tudományos munkatárs', 'Research Fellow'),
         ('posztdoktori', 'Postdoctoral Researcher'), ('tanszékvezető', 'Head of Department'),
         ('intézetigazgató', 'Institute Director'), ('dékán', 'Dean')]


def rows(html=None):
    """{posting url: (title, row text)} from the vacancy table: position,
    unit, open date, close date. The title adds the English rank."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    if html is None:
        status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    out = {}
    for tr in BeautifulSoup(html, 'html.parser').find_all('tr'):
        a = tr.find('a', href=DOC_RE)
        cells = [td.get_text(' ', strip=True) for td in tr.find_all(['td', 'th'])]
        if not a or len(cells) < 2:
            continue
        import unicodedata
        position, unit = (unicodedata.normalize('NFC', c) for c in cells[:2])   # some cells use decomposed accents
        # longest rank first: "egyetemi tanársegéd" must not match "egyetemi tanár"
        english = next((en for hu, en in sorted(RANKS, key=lambda r: -len(r[0]))
                        if position.lower().startswith(hu)), '')
        title = f'{position} ({english}), {unit}' if english else f'{position}, {unit}'
        opens, closes = (cells[2], cells[3]) if len(cells) >= 4 else ('', '')
        out[urljoin('https://www.elte.hu/', a['href'].strip())] = (
            title, f'{title}. Open date: {opens} Closing Date: {closes}')
    return out


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['nav', 'header', 'footer', 'script', 'style']):
        tag.decompose()
    main = soup.select_one('main') or soup
    links = []
    for a in main.find_all('a', href=True):
        url = urljoin('https://www.elte.hu/', a['href'].strip())
        if DOC_RE.search(url) and not FORM_RE.search(a.get_text(' ', strip=True) + ' ' + url) and url not in links:
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
