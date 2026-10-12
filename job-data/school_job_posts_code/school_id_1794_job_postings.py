"""
Job postings scraper for school_id 1794 - Charles Darwin University (Australia)
ATS platform: own website
Careers link: https://cdu.t1cloud.com/T1Default/CiAnywhere/Web/CDU/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Charles Darwin University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1794_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1794_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
CDU's board is TechnologyOne CiAnywhere, shown as a grid (Title / Name /
Employee Type). The links in the old careers link and the audit sheet carry
per-session h=/t= values and later redirect to the staff LOG ON page, so the
public entry point is used. Only the visible rows of the grid exist, so it is scrolled.
Jobs have no URL or reference of their own; each is stored as the public
board URL + "#<title slug>".
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1794
SCHOOL_NAME = 'Charles Darwin University'
CAREERS_LINK = 'https://cdu.t1cloud.com/T1Default/CiAnywhere/Web/CDU/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def board_rows():
    """[(slug, title, employee type)] for every row of the job table."""
    rows = []

    def read(page):
        # A SlickGrid: rows are div.slick-row (cells: title, name, employee
        # type) and only the visible ones exist, so the grid's viewport is
        # scrolled in steps until no new title appears.
        page.wait_for_selector('.slick-row', timeout=60000, state='attached')
        page.wait_for_timeout(3000)
        idle = 0
        for _ in range(60):
            before = len(rows)
            for row in page.query_selector_all('.slick-row'):
                cells = [c.inner_text().strip() for c in row.query_selector_all('.slick-cell')]
                if len(cells) >= 3 and cells[0]:
                    title, kind = cells[0], cells[2]
                    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                    if slug and slug not in [r[0] for r in rows]:
                        rows.append((slug, title, kind))
            idle = 0 if len(rows) > before else idle + 1
            if idle >= 3:
                break
            page.evaluate("document.querySelectorAll('.slick-viewport').forEach(v => v.scrollTop += 300)")
            page.wait_for_timeout(800)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000, actions=read, timeout=90000)
    if not rows:
        raise RuntimeError(html[:200] if html and lib.is_fetch_failure(html) else 'no job rows found')
    return rows


def find_links():
    return [f'{CAREERS_LINK}#{slug}' for slug, _title, _kind in board_rows()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
