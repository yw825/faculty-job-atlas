"""
Job postings scraper for school_id 37 - Hendrix College (US)
ATS platform: own website
Careers link: https://www.hendrix.edu/humanresources/jobs.aspx

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Hendrix College; nothing here affects any
other school's script.

Link check (review): 0 posting-shaped links found -- rendered no job-shaped links found.

TUNED FIND_LINKS
The board is Paycor (clientId 8a37b2194d086588014d30aec731052e) in an
iframe on this page; Paycor redirects back here when opened directly, so the
list is read from inside the frame. Each posting is stored in Hendrix's own
form, jobs.aspx?gnk=job&gni=<32-hex job id>, which opens that job in the
frame. paycor_frame_html() is reused by this school's info script.

Writes school_job_posts/school_id_37_job_posts.csv (school_id, post_link).
Checkpointed to school_id_37_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 37
SCHOOL_NAME = 'Hendrix College'
CAREERS_LINK = 'https://www.hendrix.edu/humanresources/jobs.aspx'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


JOB_ID_RE = re.compile(r'JobIntroduction\.action\?[^"\'<>]*?\bid=([0-9a-f]{32})', re.I)
POSTING_URL = 'https://www.hendrix.edu/humanresources/jobs.aspx?gnk=job&gni={}&lang=en'


def paycor_frame_html(url, ready_selector='a[href*="JobIntroduction"]', wait_ms=20000):
    """HTML of the Paycor iframe on a hendrix.edu page. The Paycor board
    redirects to this page when opened on its own, so it is only readable
    from inside the frame."""
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    page = b.new_page(user_agent=lib.UA)
    try:
        page.goto(url, timeout=30000, wait_until='domcontentloaded')
        frame = None
        for _ in range(wait_ms // 500):
            frame = next((f for f in page.frames if 'recruitingbypaycor.com' in f.url), None)
            if frame and frame.query_selector(ready_selector):
                break
            page.wait_for_timeout(500)
        if frame is None:
            raise RuntimeError('paycor iframe not found on ' + url)
        page.wait_for_timeout(1000)
        return frame.content()
    finally:
        page.close()


def find_links():
    html = paycor_frame_html(CAREERS_LINK)
    ids = list(dict.fromkeys(JOB_ID_RE.findall(html)))
    return [POSTING_URL.format(i) for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
