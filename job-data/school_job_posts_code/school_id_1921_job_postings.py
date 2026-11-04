"""
Job postings scraper for school_id 1921 - Ottawa University-Surprise (US)
ATS platform: Paycom (detected: paycom)
Careers link: https://www.paycomonline.net/v4/ats/web.php/portal/AB201C499D53A5D603D5BE296513B383/career-page

Ottawa University-Surprise runs on a shared ATS platform -- every school on paycom uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_paycom adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every paycom school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.

NOTE: 3 schools list against this same URL, so this listing carries every one of their postings, not just this school's: Ottawa University-Ottawa, Ottawa University-Milwaukee.

Writes school_job_posts/school_id_1921_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1921_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
All Ottawa University campuses share one Paycom board and its location
filter has no address of its own, so this campus's postings are the ones
whose location names Surprise, AZ.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1921
SCHOOL_NAME = 'Ottawa University-Surprise'
CAREERS_LINK = 'https://www.paycomonline.net/v4/ats/web.php/portal/AB201C499D53A5D603D5BE296513B383/career-page'
ATS_PLATFORM = 'Paycom'
PLATFORM = 'paycom'

PLACES = ('Surprise, AZ',)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return [url for url, _title, _type, where in lib.paycom_previews(CAREERS_LINK) if any(p in where for p in PLACES)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
