"""
Job postings scraper for school_id 104 - Pacific States University (US)
ATS platform: own website
Careers link: https://psuca.edu/jobs-opportunities/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Pacific States University; nothing here affects any
other school's script.

Link check (ok): 4 posting-shaped links found -- rendered.

TUNED FIND_LINKS
Openings are written INLINE: each is an <h3> (e.g. "Admissions Officer",
"Department Chair") followed by its description, with nothing to click
through to. Each is stored as this page plus #<slug of its heading>; the
body stops at the next <h3> or the footer's first <h4>. sections() and
page_html() are reused by this school's info script.

Writes school_job_posts/school_id_104_job_posts.csv (school_id, post_link).
Checkpointed to school_id_104_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 104
SCHOOL_NAME = 'Pacific States University'
CAREERS_LINK = 'https://psuca.edu/jobs-opportunities/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def sections(html, base_url=CAREERS_LINK):
    """[(url#slug, title, body)] -- one per <h3>, whose body runs to the next
    <h3> or to the footer's first <h4>."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()
    out = []
    for h3 in soup.find_all('h3'):
        title = h3.get_text(' ', strip=True)
        parts = []
        for node in h3.find_all_next(string=True):
            if node.find_parent(['h3', 'h4']) is not None:
                if node.find_parent('h3') is h3:
                    continue
                break
            text = node.strip()
            if text:
                parts.append(text)
        body = ' '.join(parts)
        if title and len(body) >= 200:
            out.append((f'{base_url}#{lib._slugify(title)}', title, body[:20000]))
    return out


def page_html():
    """psuca.edu sits behind a Cloudflare check, so it is always rendered."""
    return lib._fetch_rendered_retry(CAREERS_LINK, 8000)


def find_links():
    return [u for u, _t, _b in sections(page_html())]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
