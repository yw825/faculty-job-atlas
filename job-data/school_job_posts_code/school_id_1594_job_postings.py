"""
Job postings scraper for school_id 1594 - University of Northern British Columbia (Canada)
ATS platform: Njoyn
Careers link: https://unbc.njoyn.com/CL/xweb/xweb.asp?tbtoken=Y1xaSxoXCGouJS5ALiReFC4lLkAuJF4ENlRQCFQ7AmdEcFkuckggVFF%2FExYtWDVuUTUecBYuJS5ALiRecAkbVRdXQHJiF3U%3D&chk=ZVpaShM%3D&clid=125926&page=joblisting&categoryid=1385

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Northern British Columbia; nothing here affects any
other school's script.

TUNED FIND_LINKS
Njoyn board. Its job links carry a per-visit session token (tbtoken,
chk), so each posting is stored token-free as xweb.asp?clid=<clid>&
Page=JobDetails&Jobid=<id>&BRID=<id>&lang=1. The site sits behind a
Radware bot check; when it serves the block page the run errors out instead
of recording "no jobs". UNVERIFIED (2026-10-08): the token-free detail link
could not be opened while the block was up -- check one by hand.

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


def find_links():
    html = lib._fetch_rendered_retry(LISTING, 6000)
    if 'Radware' in html or 'solve this CAPTCHA' in html:
        raise RuntimeError('njoyn: blocked by the Radware bot check')
    jobs = {}
    for jid, brid in JOB_RE.findall(html):
        jobs.setdefault(jid.upper(), brid)
    # Njoyn's own links carry a per-visit tbtoken/chk; storing those would
    # mint a "new" posting on every run, so the token-free form is stored.
    return [f'https://unbc.njoyn.com/CL/xweb/xweb.asp?clid=125926&Page=JobDetails&Jobid={jid}' + (f'&BRID={brid}' if brid else '') + '&lang=1'
            for jid, brid in jobs.items()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
