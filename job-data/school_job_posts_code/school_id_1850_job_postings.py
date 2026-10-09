"""
Job postings scraper for school_id 1850 - Macao Polytechnic University (Macau)
ATS platform: own website
Careers link: https://earth.ipm.edu.mo/store/en/pre/notification/page/home

CUSTOMIZED (confirmed live): each recruitment notice is a "box" widget
containing several dated documents (Recruitment Notice, Provisional List,
Definitive List, ...) for ONE opening, ending in the literal text
"(Application closed)" once it's no longer accepting applications -- every
box shares the same CSS class regardless of status (checked directly: a
confirmed-closed box and the one open box both render as
class="box box-success", so open/closed is NOT visually distinguishable by
class, only by that trailing text). This keeps one representative link
(the first document) per box that does NOT contain that closed marker. The
generic default's job-shaped filter was separately missing the real
per-notice document links entirely (they're hash-prefixed filenames like
"11c0c-2.0-it-ts-2603-v5-upload.pdf" with no job-shaped word in them) and
picking up 3 generic application-FORM TEMPLATE links instead (reusable
blank forms, not tied to any specific opening).

Writes school_job_posts/school_id_1850_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1850_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
MPU's recruitment page has an Academic Staff tab (#tab-aca) of collapsible
boxes, one per call ("Recruitment of 8 Full-time Lecturers ... (2526-FCA-009)");
each call's "Recruitment Notice" PDF is stored. Non-academic calls (the
other tab) are not collected.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1850
SCHOOL_NAME = 'Macao Polytechnic University'
CAREERS_LINK = 'https://earth.ipm.edu.mo/store/en/pre/notification/page/home'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    status, html = lib.fetch_static(CAREERS_LINK, timeout=40)
    if status != 200:
        raise RuntimeError(f'recruitment page status={status}')
    tab = BeautifulSoup(html, 'html.parser').find(id='tab-aca')
    if tab is None:
        raise RuntimeError('academic tab not found')
    links = []
    for box in tab.select('.box'):
        items = [(li.get_text(' ', strip=True), a['href']) for li in box.select('li') for a in li.find_all('a', href=re.compile(r'\.pdf'))]
        pick = next((h for t, h in items if re.search(r'(?i)recruitment notice', t)), items[-1][1] if items else None)
        if pick:
            links.append(urljoin('https://earth.ipm.edu.mo/store/', pick))
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
