"""
Job postings scraper for school_id 1712 - LUISS Guido Carli (Italy)
Careers link: https://www.luiss.it/en/university/governance/faculty/recruitment

TUNED FIND_LINKS
LUISS lists its open faculty calls in English under Faculty > Recruitment:
"Recruitment of tenured faculty" (full/associate professor calls) and
"Recruiting researchers" (tenure-track assistant professors), each with a
"List of open calls" whose entries are /en/university/bandi/<slug> pages;
calls past their deadline are dropped; expired calls also sit on separate "past-calls" pages and are not followed. The
national MUR portal (used 2026-10-09 morning) showed only 1 of them.
Contract-teaching and research-contractor pages are not collected.

Writes school_job_posts/school_id_1712_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1712_job_postings.checkpoint next to this script.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1712
SCHOOL_NAME = 'LUISS Guido Carli'
CAREERS_LINK = 'https://www.luiss.it/en/university/governance/faculty/recruitment'
ATS_PLATFORM = 'own website'
SECTIONS = ('recruitment-tenured-faculty', 'recruiting-researchers')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from urllib.parse import urljoin
    links = []
    for section in SECTIONS:
        status, html = lib.fetch_static(f'{CAREERS_LINK}/{section}', timeout=40)
        if status != 200:
            raise RuntimeError(f'{section} status={status}')
        for href in re.findall(r'href="(/en/university/bandi/[^"#?]+)"', html):
            url = urljoin('https://www.luiss.it', href)
            if url not in links:
                links.append(url)
    # The "open" lists keep calls past their deadline (two tenure-track calls
    # closing 31 August 2026 were still listed in October), so each call's
    # "Deadline : <weekday> 15 October 2026" is checked.
    today = datetime.date.today()
    still_open = []
    for url in links:
        status, html = lib.fetch_static(url, timeout=40)
        m = re.search(r'Deadline\s*:?\s*(?:\w+day\s+)?(\d{1,2} \w+ \d{4})', re.sub(r'<[^>]+>', ' ', html or ''))
        if m:
            try:
                if datetime.datetime.strptime(m[1], '%d %B %Y').date() < today:
                    continue
            except ValueError:
                pass
        still_open.append(url)
    return still_open


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
