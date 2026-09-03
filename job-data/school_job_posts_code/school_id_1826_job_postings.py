"""
Job postings scraper for school_id 1826 - University of Otago (New Zealand)
ATS platform: Taleo (detected: taleo)
Careers link: https://otago.taleo.net/careersection/2/moresearch.ftl

CUSTOMIZED (confirmed live): this Taleo instance runs an OLDER CareerSection
template than the one job_postings_lib.scrape_taleo was built against --
every posting link is a plain href="#" with a JS onclick handler
(requisition_openRequisitionDescription(...)), not a real navigable URL, so
the shared adapter's href-based extraction finds nothing here even after
correctly clicking through to the job list ("All Jobs", not "View All
Jobs" -- also different from the variant the shared adapter expects).
Confirmed fix: each job's own requisition ID IS visible in the list text as
"Title ( 123456 )", and https://otago.taleo.net/careersection/2/jobdetail.
ftl?job=123456 (the SAME canonical URL shape the shared adapter already
builds for the newer template) resolves to a real 200 response for that
job -- so this reads the IDs straight from the rendered list text and
builds the URLs directly, bypassing the broken href search entirely.

Writes school_job_posts/school_id_1826_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1826_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1826
SCHOOL_NAME = 'University of Otago'
CAREERS_LINK = 'https://otago.taleo.net/careersection/2/moresearch.ftl'
ATS_PLATFORM = 'Taleo'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    b = lib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    page = b.new_page(user_agent=lib.UA)
    try:
        page.goto(CAREERS_LINK, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(2500)
        all_jobs = page.get_by_text('All Jobs', exact=True)
        if all_jobs.count() == 0:
            raise RuntimeError('no "All Jobs" link found -- page structure may have changed')
        all_jobs.first.click(timeout=5000)
        page.wait_for_timeout(3000)
        html = page.content()
    finally:
        page.close()
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    body_text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    job_ids = re.findall(r'\(\s*(\d{6,8})\s*\)', body_text)
    seen, links = set(), []
    for jid in job_ids:
        if jid not in seen:
            seen.add(jid)
            links.append(f'https://otago.taleo.net/careersection/2/jobdetail.ftl?job={jid}')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
