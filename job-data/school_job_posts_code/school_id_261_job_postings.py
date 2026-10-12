"""
Job postings scraper for school_id 261 - Florida State University (US)
ATS platform: own website
Careers link: https://jobs.omni.fsu.edu/psc/sprdhr_er/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Florida State University; nothing here affects any
other school's script.

Link check (ok): 5 posting-shaped links found.

Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_261_job_posts.csv (school_id, post_link).
Checkpointed to school_id_261_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
Careers link corrected in the audit to FSU's PeopleSoft job search (Fluid):
the list loads more rows as it is scrolled (226 jobs) and rows have no
link, but each carries its job id, and a posting opens at
...Page=HRS_APP_JBPST_FL&...&JobOpeningId=<id>&PostingSeq=1.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 261
SCHOOL_NAME = 'Florida State University'
CAREERS_LINK = 'https://jobs.omni.fsu.edu/psc/sprdhr_er/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    ids = []

    def scroll(page):
        stale = 0
        for _ in range(80):
            new = [x for x in re.findall(r'HRS_APP_JBSCH_I_HRS_JOB_OPENING_ID\$\d+[^>]*>(\d+)<', page.content()) if x not in ids]
            ids.extend(dict.fromkeys(new))
            stale = 0 if new else stale + 1
            if stale >= 3:
                break
            rows = page.query_selector_all('li[id*="HRS_AGNT_RSLT_I"], tr[id*="HRS_AGNT_RSLT_I"]')
            if rows:
                rows[-1].scroll_into_view_if_needed()
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2500)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=9000, actions=scroll, timeout=90000)
    if not ids:
        raise RuntimeError(html[:200] if html else 'job search did not render')
    base = CAREERS_LINK.split('?')[0]
    return [f'{base}?Page=HRS_APP_JBPST_FL&Action=U&FOCUS=Applicant&SiteId=1&JobOpeningId={i}&PostingSeq=1' for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
