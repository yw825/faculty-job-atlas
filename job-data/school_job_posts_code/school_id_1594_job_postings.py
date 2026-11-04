"""
Job postings scraper for school_id 1594 - University of Northern British Columbia (Canada)
ATS platform: Njoyn
Careers link: https://unbc.njoyn.com/CL/xweb/xweb.asp?tbtoken=Y1xaSxoXCGouJS5ALiReFC4lLkAuJF4ENlRQCFQ7AmdEcFkuckggVFF%2FExYtWDVuUTUecBYuJS5ALiRecAkbVRdXQHJiF3U%3D&chk=ZVpaShM%3D&clid=125926&page=joblisting&categoryid=1385

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Northern British Columbia; nothing here affects any
other school's script.

TUNED FIND_LINKS
Njoyn board, read with the INSTALLED Google Chrome in a visible window
(lib.get_real_chrome): Njoyn's Radware bot wall blocks the bundled headless
Chromium and headless Chrome, but passes normal Chrome -- the user's own
browser was never blocked. Requests are spaced PAUSE_MS apart. Its job links
carry a per-visit session token (tbtoken, chk), so each posting is stored
token-free as xweb.asp?clid=<clid>&Page=JobDetails&Jobid=<id>&BRID=<id>&lang=1,
which opens the same job (verified 2026-10-08). njoyn_page() is reused by
the info script.

Writes school_job_posts/school_id_1594_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1594_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1594
SCHOOL_NAME = 'University of Northern British Columbia'
CAREERS_LINK = 'https://unbc.njoyn.com/CL/xweb/xweb.asp?tbtoken=Y1xaSxoXCGouJS5ALiReFC4lLkAuJF4ENlRQCFQ7AmdEcFkuckggVFF%2FExYtWDVuUTUecBYuJS5ALiRecAkbVRdXQHJiF3U%3D&chk=ZVpaShM%3D&clid=125926&page=joblisting&categoryid=1385'
ATS_PLATFORM = 'Njoyn'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


LISTING = 'https://unbc.njoyn.com/CL/xweb/xweb.asp?clid=125926&page=joblisting&categoryid=1385'
JOB_RE = re.compile(r'Jobid=([A-Z0-9-]+)(?:&(?:amp;)?BRID=(\d+))?', re.I)


LISTING = 'https://unbc.njoyn.com/CL/xweb/xweb.asp?clid=125926&page=joblisting&categoryid=1385'
BASE = 'https://unbc.njoyn.com/CL/xweb/xweb.asp?clid=125926'
JOB_RE = re.compile(r'Jobid=([A-Z0-9-]+)(?:&(?:amp;)?BRID=(\d+))?', re.I)
PAUSE_MS = 4000          # Njoyn's bot wall reacts to bursts; keep requests apart
_last = [0.0]


def njoyn_page(url):
    """Page HTML via the installed Chrome in a visible window: Radware blocks
    the bundled headless browser (and headless Chrome) but not this."""
    import time
    wait = PAUSE_MS / 1000 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    page = lib.get_real_chrome().new_page()
    try:
        page.goto(url, timeout=45000, wait_until='domcontentloaded')
        page.wait_for_timeout(4000)
        html = page.content()
    finally:
        page.close()
        _last[0] = time.time()
    if 'Radware' in html or 'solve this CAPTCHA' in html:
        raise RuntimeError('njoyn: blocked by the Radware bot check')
    return html


def find_links():
    jobs = {}
    for jid, brid in JOB_RE.findall(njoyn_page(LISTING)):
        jobs.setdefault(jid.upper(), brid)
    # Njoyn's own links carry a per-visit tbtoken/chk; the token-free form
    # opens the same job (checked 2026-10-08) and stays stable across runs.
    return [f'{BASE}&Page=JobDetails&Jobid={jid}' + (f'&BRID={brid}' if brid else '') + '&lang=1'
            for jid, brid in jobs.items()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
