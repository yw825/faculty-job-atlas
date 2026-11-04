"""
Job postings scraper for school_id 187 - Central Connecticut State University (US)
ATS platform: PCRecruiter
Careers link: https://host.pcrecruiter.net/pcrbin/jobboard.aspx?uid=central%20connecticut%20state%20university.centralconnecticutstateuniversity

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

WHY THIS WAS REPOINTED
It used to point at https://www.ccsu.edu/hr/administrative/faculty/management
and run the generic COMMON_JOB_URL_HINTS filter over it. That page never
contains a single job: CCSU embeds its PCRecruiter board in an IFRAME,
loaded by www2.pcrecruiter.net/pcrimg/inc/pcrframehost.js, so the postings
live on host.pcrecruiter.net and are invisible to anything reading the
outer page. The old "5 posting-shaped links found" check passed because the
generic filter matched CCSU's own HR navigation (/hr/job-opportunities,
/hr/new-employee-information and the like) -- department pages, not jobs.
This was caught when a real posting the school was advertising could not be
found anywhere in the checkpoint.

THE LINK FORMAT IS A CHOICE
The board's own anchors carry an opaque session-ish token:
  ?action=detail&recordid=<N>&pcr-id=fGNlbnRyYWxjb25uZWN0aWN1dHN0YXRl...
Those are NOT used here. The same detail page is served from the stable
account id instead -- ?action=detail&recordid=<N>&uid=<uid> -- which is
verified to return the posting (recordid 125219375561299 -> "Assistant
Professor of MIS", 54 KB). A bare recordid with neither parameter returns
"Internal Error", so one of the two is required and `uid` is the one that
does not look like it expires.

The board is plain server-rendered HTML (~20 KB), so no browser is needed.

Writes school_job_posts/school_id_187_job_posts.csv (school_id, post_link).
Checkpointed to school_id_187_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 187
SCHOOL_NAME = 'Central Connecticut State University'
UID = 'central%20connecticut%20state%20university.centralconnecticutstateuniversity'
CAREERS_LINK = 'https://host.pcrecruiter.net/pcrbin/jobboard.aspx?uid=' + UID
ATS_PLATFORM = 'PCRecruiter'

RECORD_ID = re.compile(r'recordid=(\d+)')
DETAIL_URL = ('https://host.pcrecruiter.net/pcrbin/jobboard.aspx'
              '?action=detail&recordid={}&uid=' + UID)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=25)
    if status != 200 or not html:
        raise RuntimeError(f'ccsu pcrecruiter board returned http={status}')
    ids = sorted(set(RECORD_ID.findall(html)), key=int)
    if not ids:
        raise RuntimeError('ccsu pcrecruiter board listed no postings')
    return [DETAIL_URL.format(i) for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
