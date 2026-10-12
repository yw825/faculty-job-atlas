"""
Job postings scraper for school_id 1752 - University of Geneva (Switzerland)
ATS platform: own website
Careers link: https://jobs.unige.ch/www/wd_portal.search_results?p_web_site_id=1&p_category_id=1&p_show_results=Y&p_form_type=CHECKBOX&p1=51&p1_val=Any&p2=46&p2_val=Any&p_text=

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Geneva; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1752_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1752_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The search results show 10 per page (p_start=1,11,21,...); postings are wd_portal.show_job?...p_web_page_id=<n>
(not the view_blob attachments).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1752
SCHOOL_NAME = 'University of Geneva'
CAREERS_LINK = 'https://jobs.unige.ch/www/wd_portal.search_results?p_web_site_id=1&p_category_id=1&p_show_results=Y&p_form_type=CHECKBOX&p1=51&p1_val=Any&p2=46&p2_val=Any&p_text='
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    # Pages after the first only answer inside the session (cookie) that
    # loaded page 1; a fresh request gets an empty redirect stub.
    session = lib.requests.Session()
    session.headers.update({'User-Agent': lib.UA})
    ids = []
    for start in range(1, 2000, 10):
        url = CAREERS_LINK if start == 1 else f'{CAREERS_LINK}&p_start={start}&p_order_by='
        r = session.get(url, headers={'Referer': CAREERS_LINK}, timeout=40)
        if r.status_code != 200:
            if start == 1:
                raise RuntimeError(f'search status={r.status_code}')
            break
        new = [i for i in dict.fromkeys(re.findall(r'wd_portal\.show_job\?p_web_site_id=1&(?:amp;)?p_web_page_id=(\d+)', r.text)) if i not in ids]
        if not new:
            break
        ids += new
    return [f'https://jobs.unige.ch/www/wd_portal.show_job?p_web_site_id=1&p_web_page_id={i}' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
