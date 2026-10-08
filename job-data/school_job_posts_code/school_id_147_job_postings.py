"""
Job postings scraper for school_id 147 - Westmont College (US)
ATS platform: own website
Careers link: https://www.westmont.edu/office-provost/open-positions

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Westmont College; nothing here affects any
other school's script.

Link check (review): 1 posting-shaped links found -- rendered few job-shaped links.

TUNED FIND_LINKS
Openings are cards in a Salesforce "jobList" component; each card expands
(the chevron) to its full description and has no page of its own. A card
carries a stable Salesforce record id (data-job-id), so each opening is
stored as this page plus #<that id>. cards() is reused by this school's
info script to read one card back.

Writes school_job_posts/school_id_147_job_posts.csv (school_id, post_link).
Checkpointed to school_id_147_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 147
SCHOOL_NAME = 'Westmont College'
CAREERS_LINK = 'https://www.westmont.edu/office-provost/open-positions'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def cards(html, base_url=CAREERS_LINK):
    """[(url#job-id, title, description)] for every job card on the page."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for card in soup.select('.job-card'):
        header = card.select_one('[data-job-id]')
        title = card.select_one('.job-title')
        if not header or not title:
            continue
        details = card.select_one('.job-details') or card
        out.append((f"{base_url}#{header['data-job-id']}", title.get_text(' ', strip=True),
                    details.get_text(' ', strip=True)))
    return out


def rendered_page():
    """The job list is a Salesforce Lightning component that builds the
    cards client-side; wait for them rather than for a fixed time."""
    def wait_for_cards(page):
        try:
            page.wait_for_selector('.job-card', timeout=20000)
        except Exception:
            pass                      # an empty board has no cards at all
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=3000, actions=wait_for_cards)
    if not html or lib.is_fetch_failure(html):
        raise RuntimeError(html or 'westmont page did not render')
    return html


def find_links():
    return [u for u, _t, _d in cards(rendered_page())]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
