"""
Job postings scraper for school_id 1702 - University College Cork (Ireland)
ATS platform: CoreHR
Careers link: https://my.corehr.com/pls/uccrecruit/erq_search_version_4.start_search_with_params

WHY THIS SCRAPER DELIBERATELY FINDS NOTHING
It previously pointed at https://ucc.peopleadmin.com/ and ran the shared
peopleadmin adapter, which returned 176 postings. The docstring recorded
that as a discovery: "UCC also runs a PeopleAdmin tenant at
ucc.peopleadmin.com whose Atom feed lists 116 postings."

That was wrong. ucc.peopleadmin.com is titled "Jobs at UCNJ Union College
of Union County, NJ", names UCNJ's own departments, and mentions Cork zero
times. It belongs to a community college in New Jersey that happens to share
the "ucc" token. A past session hit the CoreHR 403, guessed that `ucc` meant
University College Cork on PeopleAdmin, found a live board, and wrote the
guess up as a finding -- so for weeks this school published 176 of another
institution's jobs, 133 of them titled "Jobs at UCNJ Union College of Union
County, NJ".

Cork's real board is the CoreHR tenant named in CAREERS_LINK, and it answers
every request with HTTP 403 -- as does every other CoreHR tenant tried,
including Oxford's. So this school has no scrapeable route, exactly like
Dublin City University and University of Galway, whose candidate hostnames
do not resolve at all.

The point of raising rather than silently returning an empty list: a school
that yields nothing because its board is blocked should look blocked in the
run log, not look like a scraper whose find_links() needs tuning. The 403 is
recorded in the checkpoint's last_error where it can be read.

If a genuine UCC board is ever found, the test it must pass is simple: the
page names University College Cork, not merely a host containing "ucc".

Writes school_job_posts/school_id_1702_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1702_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1702
SCHOOL_NAME = 'University College Cork'
CAREERS_LINK = ('https://my.corehr.com/pls/uccrecruit/'
                'erq_search_version_4.start_search_with_params')
ATS_PLATFORM = 'CoreHR'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=20)
    if status != 200 or not html:
        raise RuntimeError(
            f'ucc corehr board returned http={status} -- CoreHR blocks every '
            f'tenant tried; no scrapeable route for this school')
    # Reached only if CoreHR ever stops blocking: whatever is parsed here must
    # be verified to name University College Cork before it is trusted.
    raise RuntimeError('ucc corehr board responded 200 unexpectedly -- '
                       'verify it is Cork, then implement parsing')


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
