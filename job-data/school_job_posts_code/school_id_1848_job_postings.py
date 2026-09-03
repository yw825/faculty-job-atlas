"""
Job postings scraper for school_id 1848 - UOW College Hong Kong (Hong Kong)
ATS platform: own website
Careers link: https://www.uowchk.edu.hk/working-with-us/

CUSTOMIZED (confirmed live): postings are listed as accordion items, one
per opening, with NO real posting URL at all -- applications go by email
(a mailto: link is the only other href in each item) and the only other
link is the accordion's own in-page tab anchor (e.g. "#tab-136080"). That
tab anchor is at least unique and stable per posting (Foundation
accordion), so it's used here as the posting_url, resolved against the
page's own URL. The same accordion list also holds 4 non-posting
informational sections ("About UOW College Hong Kong", "Notes to
Applicants", "Job Applications", "Human Resources Office Location") mixed
in with the 9 real openings -- filtered out by requiring the item's title
to contain a rank/role word, which none of those four do.

Writes school_job_posts/school_id_1848_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1848_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1848
SCHOOL_NAME = 'UOW College Hong Kong'
CAREERS_LINK = 'https://www.uowchk.edu.hk/working-with-us/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

ROLE_WORD_RE = re.compile(r'\b(lecturers?|professors?|instructors?|officers?|clerical|assistant|associate)\b', re.I)


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for item in soup.find_all('li', class_='accordion-item'):
        tab_link = item.find('a', href=lambda h: h and h.startswith('#tab-'))
        if not tab_link:
            continue
        title = tab_link.get_text(' ', strip=True)
        if ROLE_WORD_RE.search(title):
            links.append(lib.urljoin(CAREERS_LINK, tab_link['href']))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
