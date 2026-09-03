"""
Job postings scraper for school_id 1833 - HKCT Institute of Higher Education (Hong Kong)
ATS platform: own website
Careers link: https://www.hkct.edu.hk/en/abouthkct/join-us

CUSTOMIZED (confirmed live): this one page lists BOTH academic and
non-academic openings, in two separate collapsible sections ("Academic
posts" / "Non-academic posts"), each already present in the raw DOM (the
"collapse" only toggles CSS visibility). Real posting links carry
university-internal reference codes as their URL slug (e.g. .../dss-hd),
not a job-shaped keyword the generic default would catch, and the
non-academic section would double the count if not excluded -- so this
scopes strictly to the section with id="academic".

Writes school_job_posts/school_id_1833_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1833_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1833
SCHOOL_NAME = 'HKCT Institute of Higher Education'
CAREERS_LINK = 'https://www.hkct.edu.hk/en/abouthkct/join-us'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    academic_section = soup.find(id='academic')
    if not academic_section:
        raise RuntimeError('no #academic section found -- page structure may have changed')
    links, seen = [], set()
    for item in academic_section.find_all(class_='item-title'):
        a = item.find_parent('a', href=True)
        if not a:
            continue
        full = lib.urljoin(CAREERS_LINK, a['href'])
        if full not in seen:
            seen.add(full)
            links.append(full)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
