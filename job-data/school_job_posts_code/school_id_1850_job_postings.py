"""
Job postings scraper for school_id 1850 - Macao Polytechnic University (Macau)
ATS platform: own website
Careers link: https://earth.ipm.edu.mo/store/en/pre/notification/page/home

CUSTOMIZED (confirmed live): each recruitment notice is a "box" widget
containing several dated documents (Recruitment Notice, Provisional List,
Definitive List, ...) for ONE opening, ending in the literal text
"(Application closed)" once it's no longer accepting applications -- every
box shares the same CSS class regardless of status (checked directly: a
confirmed-closed box and the one open box both render as
class="box box-success", so open/closed is NOT visually distinguishable by
class, only by that trailing text). This keeps one representative link
(the first document) per box that does NOT contain that closed marker. The
generic default's job-shaped filter was separately missing the real
per-notice document links entirely (they're hash-prefixed filenames like
"11c0c-2.0-it-ts-2603-v5-upload.pdf" with no job-shaped word in them) and
picking up 3 generic application-FORM TEMPLATE links instead (reusable
blank forms, not tied to any specific opening).

Writes school_job_posts/school_id_1850_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1850_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1850
SCHOOL_NAME = 'Macao Polytechnic University'
CAREERS_LINK = 'https://earth.ipm.edu.mo/store/en/pre/notification/page/home'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # This page declares <base href="https://earth.ipm.edu.mo/store/"/>, so
    # relative hrefs ("./uploads/...") must resolve against THAT, not
    # against CAREERS_LINK itself -- confirmed live: resolving against
    # CAREERS_LINK (the plain, correct approach on any page without a
    # <base> tag) produced a URL that 500'd; the browser's own
    # base-tag-aware resolution (el.href) gave the real, 200-status PDF URL.
    base_tag = soup.find('base', href=True)
    base_url = base_tag['href'] if base_tag else CAREERS_LINK
    links = []
    for box in soup.find_all('div', class_='box'):
        if 'application closed' in box.get_text(' ', strip=True).lower():
            continue
        a = box.find('a', href=True)
        if a:
            links.append(lib.urljoin(base_url, a['href']))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
