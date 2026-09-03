"""
Job postings scraper for school_id 1634 - York University (Canada)
ATS platform: own website
Careers link: https://www.yorku.ca/vpepc/faculty-affairs/faculty-positions/

CUSTOMIZED (confirmed live): postings are listed inside a "All Available
Faculty Positions" accordion, one section per faculty/school. The links are
already present in the raw DOM at page load (the accordion only toggles CSS
visibility, doesn't inject content on click), but the generic default's
job-shaped filter misses them -- each posting is a link straight to a PDF
(e.g. ".../wp-content/uploads/sites/698/2026/08/HUMA.LAPS_IndStud.pdf")
whose href has no job-shaped keyword in it at all, and whose link text is a
plain rank+title ("Assistant Professor - Indigenous Women and Cultures of
Resistance") with no "job/career/posting" word either. Broadening the
site-wide default to catch "Professor"/"Faculty" would flood every other
school's default with nav noise (this page alone has "Faculty & Staff",
"Faculty Affairs", "Faculty Recruitment" as unrelated nav links), so this is
scoped to just the accordion's own content area instead: every link inside
a kt-accordion-panel-inner block, excluding the ">>Visit the X website"
per-faculty nav links that live in the same panels.

Writes school_job_posts/school_id_1634_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1634_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1634
SCHOOL_NAME = 'York University'
CAREERS_LINK = 'https://www.yorku.ca/vpepc/faculty-affairs/faculty-positions/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links, seen = [], set()
    for panel in soup.find_all(class_='kt-accordion-panel-inner'):
        for a in panel.find_all('a', href=True):
            text = a.get_text(' ', strip=True)
            if text.startswith('>>'):
                continue  # "Visit the X website" -- a faculty homepage link, not a posting
            full = lib.urljoin(CAREERS_LINK, a['href'])
            if full not in seen:
                seen.add(full)
                links.append(full)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
