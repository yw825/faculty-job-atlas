"""
Job postings scraper for school_id 1734 - Universidade de Lisboa (Portugal)
Careers link: https://www.ulisboa.pt/en/info/recruitment

TUNED FIND_LINKS
ULisboa's recruitment list covers every school of the university (Técnico,
Faculties of Sciences, Medicine, Law, ...): pages ?page=0.. of
/en/recrutamento/<edital> calls, newest first. Each call page states the
Professional Category, Unit and Deadline (dd/mm/yyyy); calls past their
deadline are skipped, and since the list is newest first, paging stops after
8 closed calls in a row. The old scraper stored the edital PDFs instead of
the call pages (the user's example is a call page).

Writes school_job_posts/school_id_1734_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1734_job_postings.checkpoint next to this script.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1734
SCHOOL_NAME = 'Universidade de Lisboa'
CAREERS_LINK = 'https://www.ulisboa.pt/en/info/recruitment'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    today = datetime.date.today()
    calls = []
    for page in range(0, 20):
        status, html = lib.fetch_static(f'{CAREERS_LINK}?page={page}', timeout=40)
        if status != 200:
            if page == 0:
                raise RuntimeError(f'recruitment list status={status}')
            break
        new = [h for h in re.findall(r'href="(/en/recrutamento/[^"#?]+)"', html) if h not in calls]
        if not new:
            break
        calls += new
    links, closed_run = [], 0
    for path in calls:
        url = 'https://www.ulisboa.pt' + path
        status, html = lib.fetch_static(url, timeout=40)
        m = re.search(r'Deadline\s*</[^>]+>\s*(?:<[^>]+>\s*)*(\d{2})/(\d{2})/(\d{4})', html or '') \
            or re.search(r'Deadline\D{0,200}?(\d{2})/(\d{2})/(\d{4})', re.sub(r'<[^>]+>', ' ', html or ''))
        if m and datetime.date(int(m[3]), int(m[2]), int(m[1])) < today:
            closed_run += 1
            if closed_run >= 8:
                break
            continue
        closed_run = 0
        links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
