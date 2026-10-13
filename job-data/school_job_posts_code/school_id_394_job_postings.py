"""
Job postings scraper for school_id 394 - Illinois College (US)
ATS platform: own website
Careers link: https://www.ic.edu/employment

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Illinois College; nothing here affects any
other school's script.

Link check (ok): 6 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_394_job_posts.csv (school_id, post_link).
Checkpointed to school_id_394_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The employment page embeds the college's Paycom board (the audit's example
is a posting there); the board is read directly.
The employment page links its faculty openings directly (they are not on the
public list of the college's Paycom board) and embeds the board for the
rest; both are read.
The employment page links its faculty openings directly (they are not on the
public list of the college's Paycom board) and embeds the board for the
rest; both are read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 394
SCHOOL_NAME = 'Illinois College'
CAREERS_LINK = 'https://www.ic.edu/employment'
ATS_PLATFORM = 'own website'

BOARD = 'https://www.paycomonline.net/v4/ats/web.php/portal/1A1F01429B0D77840F84E7C37F0997E7/career-page'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    listed = [f'https://www.paycomonline.net{p}' for p in re.findall(r'paycomonline\.net(/v4/ats/web\.php/portal/[A-Za-z0-9]+/jobs/\d+)', html)]
    return list(dict.fromkeys(listed + [row[0] for row in lib.paycom_previews(BOARD)]))


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
