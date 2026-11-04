"""
Job postings scraper for school_id 1601 - University of Manitoba (Canada)
ATS platform: own website
Careers link: https://viprecprod.ad.umanitoba.ca/A

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Manitoba; nothing here affects any
other school's script.

TUNED FIND_LINKS
The VIP recruiting site builds every link from the session
(RestoreSession-ControlURL-1?id=...), so no posting has a stable URL of its
own. Each job row does carry a fixed "Requisition No: <n>", so each posting
is stored as this listing plus #req-<n>, and its title and row text (type,
campus, posting date) are what the info script reads back via rows().

Writes school_job_posts/school_id_1601_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1601_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1601
SCHOOL_NAME = 'University of Manitoba'
CAREERS_LINK = 'https://viprecprod.ad.umanitoba.ca/A'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


REQ_RE = re.compile(r'Requisition No:\s*(\d+)', re.I)


def rows(html, base_url=CAREERS_LINK):
    """[(listing#req-N, title, row text)] -- one per job row. Titles are in
    the cell before the "Requisition No: N - Category: ..." line; the row
    text (type, campus, posting date) is everything up to the next title."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    cells = [s.strip() for s in soup.stripped_strings]
    out, seen = [], set()
    for i, cell in enumerate(cells):
        m = REQ_RE.search(cell)
        if not m or m.group(1) in seen or i == 0:
            continue
        seen.add(m.group(1))
        title = cells[i - 1]
        rest = []
        for nxt in cells[i:i + 12]:
            if nxt != cell and REQ_RE.search(nxt):
                break
            rest.append(nxt)
        out.append((f'{base_url}#req-{m.group(1)}', title, ' | '.join([title] + rest)))
    return out


def page_html():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 7000)
    if not REQ_RE.search(html):
        raise RuntimeError('umanitoba: job list did not render')
    return html


def find_links():
    return [u for u, _t, _r in rows(page_html())]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
