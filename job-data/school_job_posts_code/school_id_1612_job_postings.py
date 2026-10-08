"""
Job postings scraper for school_id 1612 - Dalhousie University (Canada)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://dal.peopleadmin.ca/postings/search?query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search

Dalhousie University runs on a shared ATS platform -- every school on peopleadmin uses the
exact same underlying site software, so this calls the shared
job_postings_lib.scrape_peopleadmin adapter rather than duplicating
platform-specific API logic here. If results for this ONE school still need
a tweak that shouldn't apply to every peopleadmin school, override find_links
below instead of editing the shared adapter.

TUNED FIND_LINKS
PeopleAdmin. The board's own Faculty filter (position_type 3, in this
link) listed 3 jobs on 2026-10-07 and omitted a tenure-stream chair, so it
is not used. Every posting in the host's Atom feed is read instead and
kept when its Posting Number marks it academic: F... (faculty) or PTAP...
(part-time academic, postdoctoral). Staff (S...) and facilities (FM...)
are dropped. Dalhousie re-lists a posting under new ids (the Maritime Law
chair appeared as 22277, 22305 and 22314), so ids are not stable over time.

Writes school_job_posts/school_id_1612_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1612_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1612
SCHOOL_NAME = 'Dalhousie University'
CAREERS_LINK = 'https://dal.peopleadmin.ca/postings/search?query=&query_v0_posted_at_date=&query_position_type_id%5B%5D=3&435=&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


ACADEMIC_NUMBER_RE = re.compile(r'Posting Number\s+(?:F\d|PTAP)', re.I)


def is_academic(url):
    status, html = lib.fetch_static(url, timeout=30)
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html or ''))
    return status == 200 and bool(ACADEMIC_NUMBER_RE.search(text))


def find_links():
    from concurrent.futures import ThreadPoolExecutor
    every = lib.scrape_peopleadmin(CAREERS_LINK)
    with ThreadPoolExecutor(6) as pool:
        keep = list(pool.map(is_academic, every))
    return [u for u, ok in zip(every, keep) if ok]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
