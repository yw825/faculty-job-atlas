"""
Job postings scraper for school_id 1701 - University of Iceland (Iceland)
ATS platform: own website
Careers link: https://english.hi.is/about-ui/working-ui/vacancies

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Iceland; nothing here affects any
other school's script.

TUNED FIND_LINKS
Openings are written INLINE: each vacancy is a div whose id is a slug of
its title, holding the title and a "Further information" accordion with
the full ad. Each is stored as this page plus #<that id>; vacancies() is
reused by the info script to read one back.

Writes school_job_posts/school_id_1701_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1701_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1701
SCHOOL_NAME = 'University of Iceland'
CAREERS_LINK = 'https://english.hi.is/about-ui/working-ui/vacancies'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def vacancies(html, base_url=CAREERS_LINK):
    """[(page#id, title, text)] -- each vacancy is a div with its own id
    (a slug of the title) inside the vacancies section."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for section in soup.select('qz-section.paragraph--vacancies'):
        for item in section.find_all('div', id=True):
            heading = item.find(['h2', 'h3'])
            title = heading.get_text(' ', strip=True) if heading else ''
            text = item.get_text(' ', strip=True)
            if title and title.lower() != 'further information' and len(text) > 300:
                url = f"{base_url}#{item['id']}"
                if url not in [u for u, _t, _x in out]:
                    out.append((url, title, re.sub(r'\s+', ' ', text)[:20000]))
    return out


def page_html():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or 'paragraph--vacancies' not in (html or ''):
        html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    return html


def find_links():
    return [u for u, _t, _x in vacancies(page_html())]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
