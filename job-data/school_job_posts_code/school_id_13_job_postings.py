"""
Job postings scraper for school_id 13 - University of Alabama in Huntsville (US)
ATS platform: own website
Careers link: https://www.uah.edu/hr/careers/faculty-careers

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Alabama in Huntsville; nothing here affects any
other school's script.

Link check (ok): 4 posting-shaped links found.

TUNED FIND_LINKS
Openings are written INLINE, grouped under one <h2> per college
(#CAHS, #BUS, #education, #engineering, #NUR, #COS, #LIB). Each opening is
a centered all-bold title line (plus an optional college/department line)
followed by its description, so every opening is stored as this page plus
#<slug of its title>. sections() is also what this school's info script
uses to read one opening back, so both sides split the page identically.

Writes school_job_posts/school_id_13_job_posts.csv (school_id, post_link).
Checkpointed to school_id_13_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 13
SCHOOL_NAME = 'University of Alabama in Huntsville'
CAREERS_LINK = 'https://www.uah.edu/hr/careers/faculty-careers'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


_BANNER_RE = re.compile(r'\bPOSITIONS\s*$', re.I)


def _is_title_line(p):
    if p.name != 'p' or 'center' not in (p.get('style') or ''):
        return False
    text = p.get_text(' ', strip=True)
    strong = ' '.join(s.get_text(' ', strip=True) for s in p.find_all(['strong', 'b']))
    return bool(text) and strong.strip() == text


def sections(html, base_url=CAREERS_LINK):
    """[(url#slug, title, body)] -- one per opening. A title is a run of
    consecutive centered all-bold paragraphs; "...POSITIONS" banners are
    dropped from it and a second line (college/department) is appended."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('.com-content-article__body') or soup
    out, block, body, title = [], [], [], None

    def flush():
        if title and sum(len(t) for t in body) > 200:
            slug = lib._slugify(title[0])
            if slug not in {u.rsplit('#', 1)[1] for u, _t, _b in out}:
                out.append((f'{base_url}#{slug}', ', '.join(title), ' '.join(body)[:20000]))

    for el in article.find_all(['p', 'h2', 'ul', 'ol', 'div'], recursive=False):
        if el.name == 'h2' or (el.name == 'div' and 'scroll-top' in (el.get('class') or [])):
            block = []
            continue
        if _is_title_line(el):
            if not block:
                flush()
                title, body = None, []
            block.append(el.get_text(' ', strip=True))
            continue
        text = el.get_text(' ', strip=True)
        if block:
            lines = [b for b in block if not _BANNER_RE.search(b)]
            if lines:
                title = lines[:2]
            block = []
        if title and text:
            body.append(text)
    flush()
    return out


_BANNER_RE = re.compile(r'\bPOSITIONS\s*$', re.I)


def _is_title_line(p):
    if p.name != 'p' or 'center' not in (p.get('style') or ''):
        return False
    text = p.get_text(' ', strip=True)
    strong = ' '.join(s.get_text(' ', strip=True) for s in p.find_all(['strong', 'b']))
    return bool(text) and strong.strip() == text


def sections(html, base_url=CAREERS_LINK):
    """[(url#slug, title, body)] -- one per opening. A title is a run of
    consecutive centered all-bold paragraphs; "...POSITIONS" banners are
    dropped from it and a second line (college/department) is appended."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('.com-content-article__body') or soup
    out, block, body, title = [], [], [], None

    def flush():
        if title and sum(len(t) for t in body) > 200:
            slug = lib._slugify(title[0])
            if slug not in {u.rsplit('#', 1)[1] for u, _t, _b in out}:
                out.append((f'{base_url}#{slug}', ', '.join(title), ' '.join(body)[:20000]))

    for el in article.find_all(['p', 'h2', 'ul', 'ol', 'div'], recursive=False):
        if el.name == 'h2' or (el.name == 'div' and 'scroll-top' in (el.get('class') or [])):
            flush()
            block, title, body = [], None, []
            continue
        if _is_title_line(el):
            if not block:
                flush()
                title, body = None, []
            block.append(el.get_text(' ', strip=True))
            continue
        text = el.get_text(' ', strip=True)
        if block:
            lines = [b for b in block if not _BANNER_RE.search(b)]
            if lines:
                title = lines[:2]
            block = []
        if title and text:
            body.append(text)
    flush()
    return out


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(CAREERS_LINK, 4000)
    return [u for u, _t, _b in sections(html)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
