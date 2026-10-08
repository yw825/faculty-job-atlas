"""
Job postings scraper for school_id 1591 - Simon Fraser University (Canada)
ATS platform: own website
Careers link: https://www.sfu.ca/vpacademic/academic-careers/current-openings.html

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Simon Fraser University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps. Current Openings links one page per faculty (faculty-positions/
<faculty>.html) plus administrative and research-chair pages. On those
pages each opening is a collapsible section -- the title in a div.toggle,
the ad in the div.toggleContent after it (e.g. "Lecturer - Innovation &
Entrepreneurship" on the Beedie page) -- so each is stored as that page
plus #<slug of its title>. A research-chair page with no sections is
itself one posting. toggles() and page() are reused by the info script.

Writes school_job_posts/school_id_1591_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1591_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1591
SCHOOL_NAME = 'Simon Fraser University'
CAREERS_LINK = 'https://www.sfu.ca/vpacademic/academic-careers/current-openings.html'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


BASE = 'https://www.sfu.ca/vpacademic/academic-careers/'
HUB_RE = re.compile(r'^https://www\.sfu\.ca/vpacademic/academic-careers/'
                    r'(?:faculty-positions/[^/?#]+\.html|administrative-appointments\.html|'
                    r'current-canada-research-chair-opportunities/[^/?#]+\.html)$', re.I)
CHAIR_PAGE_RE = re.compile(r'/current-canada-research-chair-opportunities/[^/?#]+\.html$', re.I)


def toggles(html, page_url):
    """[(page#slug, title, body)] for each collapsible posting on a page:
    a div.toggle holding the title; its div.toggleContent is the next one
    in the page (each sits in its own wrapper, so they are not siblings)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for toggle in soup.select('.main_content div.toggle'):
        title = toggle.get_text(' ', strip=True)
        content = toggle.find_next('div', class_='toggleContent')
        body = content.get_text(' ', strip=True) if content else ''
        if title and len(body) >= 200:
            slug, n = lib._slugify(title), 2
            while any(u.endswith('#' + slug) for u, _t, _b in out):
                slug, n = f'{lib._slugify(title)}-{n}', n + 1
            out.append((f'{page_url}#{slug}', title, body[:20000]))
    return out


def page(url):
    status, html = lib.fetch_static(url, timeout=30)
    if status != 200 or not html:
        html = lib._fetch_rendered_retry(url, 4000)
    return html


def find_links():
    hubs = [u for u in lib.extract_links(page(CAREERS_LINK), CAREERS_LINK) if HUB_RE.search(u)]
    links = []
    for hub in dict.fromkeys(hubs):
        sections = toggles(page(hub), hub)
        if sections:
            links.extend(u for u, _t, _b in sections if u not in links)
        elif CHAIR_PAGE_RE.search(hub) and hub not in links:
            links.append(hub)          # a research-chair ad is a page of its own
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
