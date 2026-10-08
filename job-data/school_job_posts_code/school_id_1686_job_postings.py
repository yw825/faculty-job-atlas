"""
Job postings scraper for school_id 1686 - Humboldt University of Berlin (Germany)
ATS platform: own website
Careers link: https://www.hu-berlin.de/en/university/working-at-the-hu/jobs?tx_sitepackage_joblist%5Baction%5D=search&tx_sitepackage_joblist%5Bcontroller%5D=Job&tx_sitepackage_joblist%5Bconstraint%5D%5BenableInternalOffers%5D=&tx_sitepackage_joblist%5Bt%5D=1787951974181

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Humboldt University of Berlin; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is /working-at-the-hu/jobs/details/<slug>. hu-berlin.de is
behind Anubis, a proof-of-work bot check: the browser solves it and the
page then reloads with the job list, so the scraper waits (up to 45 s) for
a job link to appear, and reports an error rather than "no jobs" if the
challenge never clears.

Writes school_job_posts/school_id_1686_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1686_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1686
SCHOOL_NAME = 'Humboldt University of Berlin'
CAREERS_LINK = 'https://www.hu-berlin.de/en/university/working-at-the-hu/jobs?tx_sitepackage_joblist%5Baction%5D=search&tx_sitepackage_joblist%5Bcontroller%5D=Job&tx_sitepackage_joblist%5Bconstraint%5D%5BenableInternalOffers%5D=&tx_sitepackage_joblist%5Bt%5D=1787951974181'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.hu-berlin\.de/en/university/working-at-the-hu/jobs/details/[^/?#]+$', re.I)


POSTING_RE = re.compile(r'^https://www\.hu-berlin\.de/en/university/working-at-the-hu/jobs/details/[^/?#]+$', re.I)
LISTING = 'https://www.hu-berlin.de/en/university/working-at-the-hu/jobs'


def _attempt():
    def wait_for_jobs(page):
        # hu-berlin.de sits behind Anubis: the first response is a
        # proof-of-work page that solves itself and then loads the real one
        try:
            page.wait_for_selector('a[href*="/jobs/details/"]', timeout=45000)
        except Exception:
            pass
    html = lib.fetch_rendered(LISTING, wait_ms=2000, actions=wait_for_jobs, timeout=45000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    links = [u for u in dict.fromkeys(lib.extract_links(html, LISTING)) if POSTING_RE.search(u)]
    if not links and 'anubis' in html.lower():
        raise RuntimeError('hu-berlin: still on the Anubis challenge page')
    return links


def find_links():
    # the proof-of-work page sometimes fails to clear on a busy run; a
    # second fresh attempt usually gets through
    try:
        return _attempt()
    except RuntimeError:
        lib.reset_browser()
        return _attempt()


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
