"""
Job postings scraper for school_id 1758 - Bilkent University (Turkey)
ATS platform: own website
Careers link: https://w3.bilkent.edu.tr/bilkent/open-academic-positions/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Bilkent University; nothing here affects any
other school's script.

CUSTOMIZED (confirmed live): the whole faculty is listed on this ONE page --
a flat table of every department, each linking straight to that opening's
application form on stars.bilkent.edu.tr/staffapp/<code>. No department-page
clicking needed despite each link's visible text reading like a department
name ("Department of Chemistry") rather than a job title -- that text would
make the generic default filter miss most of these (it doesn't read as
job/vacancy-shaped), so this filters on the destination host instead. A
department with more than one open track lists a second link as bare "1"/
"2" text right next to the named one -- also on stars.bilkent.edu.tr, so the
href-only filter catches those too, unlike a text-based one.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1758
SCHOOL_NAME = 'Bilkent University'
CAREERS_LINK = 'https://w3.bilkent.edu.tr/bilkent/open-academic-positions/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

APPLICATION_LINK_RE = re.compile(r'stars\.bilkent\.edu\.tr/staffapp/', re.I)


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK, href_pattern=APPLICATION_LINK_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
