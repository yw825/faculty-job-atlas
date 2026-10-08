"""
Job postings scraper for school_id 1619 - McMaster University (Canada)
ATS platform: own website
Careers link: https://careers.mcmaster.ca/psp/prcsprd/EMPLOYEE/HRMS/c/HRS_HRAM.HRS_APP_SCHJOB.GBL?Page=HRS_APP_SCHJOB&Action=U&FOCUS=Applicant&SiteId=1000&cmd=uninav&Rnode=HRMS&uninavpath=Root{PORTAL_ROOT_OBJECT}.Portal%20Objects{PORTAL_BASE_DATA}.Navigation%20Collections{CO_NAVIGATION_COLLECTIONS}.Custom%20Tabs{PAPP_CUSTOM_TABS}&customTab=MCM_TAB_FACULTY_POS&IgnoreParamTempl=customTab

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for McMaster University; nothing here affects any
other school's script.

TUNED FIND_LINKS
McMaster's faculty tab is a classic PeopleSoft job search inside the
portal (frame HRS_APP_SCHJOB). Postings open via postback only and the
PeopleSoft deep link (Page=HRS_APP_JBPST&JobOpeningId=...) demands a
sign-in, so no posting has a stable URL. Each row's title ends with its Job
ID ("... - 78991"), so each posting is stored as this listing plus
#job-<id>; rows() walks the 25-per-page list with the "next" postback in
one session, and the info script reads title/department/location/posted
date from the row.

Writes school_job_posts/school_id_1619_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1619_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1619
SCHOOL_NAME = 'McMaster University'
CAREERS_LINK = 'https://careers.mcmaster.ca/psp/prcsprd/EMPLOYEE/HRMS/c/HRS_HRAM.HRS_APP_SCHJOB.GBL?Page=HRS_APP_SCHJOB&Action=U&FOCUS=Applicant&SiteId=1000&cmd=uninav&Rnode=HRMS&uninavpath=Root{PORTAL_ROOT_OBJECT}.Portal%20Objects{PORTAL_BASE_DATA}.Navigation%20Collections{CO_NAVIGATION_COLLECTIONS}.Custom%20Tabs{PAPP_CUSTOM_TABS}&customTab=MCM_TAB_FACULTY_POS&IgnoreParamTempl=customTab'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


TITLE_RE = re.compile(r'^Display details of (.+?)\s*-\s*(\d+)\s*$')
COUNTER_RE = re.compile(r'(\d+)-(\d+) of (\d+)')


def rows():
    """[(listing#job-<id>, title, row text)] for every faculty posting. The
    list lives in a PeopleSoft frame inside the portal and pages 25 at a
    time through a postback "next" button, so it is walked in one session."""
    from bs4 import BeautifulSoup
    b = lib.get_browser()
    page = b.new_page(user_agent=lib.UA)
    out, seen = [], set()
    try:
        page.goto(CAREERS_LINK, timeout=45000, wait_until='domcontentloaded')
        frame = None
        for _ in range(40):
            frame = next((f for f in page.frames if 'matches found' in f.content()), None)
            if frame:
                break
            page.wait_for_timeout(500)
        if frame is None:
            raise RuntimeError('mcmaster: job list frame did not load')
        for _ in range(20):
            soup = BeautifulSoup(frame.content(), 'html.parser')
            for a in soup.select('a[id^="POSTINGLINK$"]'):
                m = TITLE_RE.match(a.get('title') or '')
                if not m or m.group(2) in seen:
                    continue
                seen.add(m.group(2))
                row = a.find_parent('tr', id=re.compile(r'^trHRS_AGNT_RSLT_I'))
                text = re.sub(r'\s+', ' ', row.get_text(' ', strip=True)) if row else m.group(1)
                out.append((f'{CAREERS_LINK}#job-{m.group(2)}', m.group(1), text))
            counter = COUNTER_RE.search(soup.get_text(' ', strip=True))
            if not counter or int(counter.group(2)) >= int(counter.group(3)):
                break
            before = counter.group(0)
            frame.click('a[id="HRS_AGNT_RSLT_I$hdown$0"]')
            for _ in range(40):
                page.wait_for_timeout(500)
                now = COUNTER_RE.search(BeautifulSoup(frame.content(), 'html.parser').get_text(' ', strip=True))
                if now and now.group(0) != before:
                    break
    finally:
        page.close()
    return out


def find_links():
    return [u for u, _t, _x in rows()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
