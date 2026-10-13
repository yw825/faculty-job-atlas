"""
Job postings scraper for school_id 340 - Maharishi International University (US)
ATS platform: own website
Careers link: https://services.miu.edu/human-resources/faculty/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Maharishi International University; nothing here affects any
other school's script.

Link check (review): 0 posting-shaped links found -- rendered no job-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_340_job_posts.csv (school_id, post_link).
Checkpointed to school_id_340_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Faculty openings are blocks of one page, each opening "POSITION TITLE:"
(the audit's example is that page). Stored as the page plus #<title slug>.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 340
SCHOOL_NAME = 'Maharishi International University'
CAREERS_LINK = 'https://services.miu.edu/human-resources/faculty/'
ATS_PLATFORM = 'own website'

POSITIONS_PAGE = 'https://services.miu.edu/human-resources/faculty/faculty-positions-available/'


def positions():
    """[(slug, title, text)] -- every advert on the page opens "POSITION TITLE:"."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(lib._fetch_rendered_retry(POSITIONS_PAGE, 5000), 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    text = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
    out = []
    for block in re.split(r'(?=POSITION TITLE:)', text)[1:]:
        m = re.match(r'POSITION TITLE:\s*(.+?)\s+(?:DUTIES|REQUIREMENTS|QUALIFICATIONS|DEPARTMENT|LOCATION)\b', block)
        title = (m.group(1) if m else block[15:95]).strip(' :-')
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80] or 'position'
        if slug in [s for s, _t, _b in out]:
            slug = f'{slug}-{len(out) + 1}'
        out.append((slug, title, block[:20000]))
    return out

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [f'{POSITIONS_PAGE}#{slug}' for slug, _t, _b in positions()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
