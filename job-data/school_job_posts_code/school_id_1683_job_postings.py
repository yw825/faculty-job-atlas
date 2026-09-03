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

SLUG_RE = re.compile(r'^/[a-z0-9]{8,12}$')
LAST_PAGE_RE = re.compile(r'[?&]page=(\d+)')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup

    def page_links(page_html, base_url):
        soup = BeautifulSoup(page_html, 'html.parser')
        out = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            path = lib.urlsplit(href).path or href
            if SLUG_RE.match(path):
                out.append(lib.urljoin(base_url, href))
        return out

    soup = BeautifulSoup(html, 'html.parser')
    last_page = 0
    for a in soup.find_all('a', href=True):
        m = LAST_PAGE_RE.search(a['href'])
        if m:
            last_page = max(last_page, int(m.group(1)))

    seen, links = set(), []
    for u in page_links(html, CAREERS_LINK):
        if u not in seen:
            seen.add(u)
            links.append(u)
    for page_num in range(1, last_page + 1):
        page_url = f'{CAREERS_LINK}?page={page_num}'
        page_html = lib.fetch_rendered(page_url)
        if lib.is_fetch_failure(page_html):
            continue
        for u in page_links(page_html, page_url):
            if u not in seen:
                seen.add(u)
                links.append(u)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
