"""
Job postings scraper for school_id 1902 - SKEMA Business School (France)
ATS platform: own website
Careers link: https://recrutement.skema.edu/?page=advertisement

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

SKEMA runs its own small PHP recruiting board. The whole listing is in the
static HTML (~15 KB, no JS), so this fetches statically rather than paying
for a render. Each advert is linked as `?page=advertisement_display&id=N`,
so the ids are harvested and rebuilt into canonical URLs -- the raw hrefs
come back HTML-escaped (`&amp;id=`), which is why the pattern tolerates the
entity but the emitted link never contains it.

Note the board root and `?page=advertisement` return byte-identical pages;
the explicit `?page=advertisement` form is used as the careers link so the
intent is legible.

At the time of writing this yields 10 adverts, essentially all faculty
("Assistant Professor in Accounting / Data Science / Finance / Marketing /
Optimization or Game Theory / Sustainability").

Writes school_job_posts/school_id_1902_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1902_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1902
SCHOOL_NAME = 'SKEMA Business School'
CAREERS_LINK = 'https://recrutement.skema.edu/?page=advertisement'
ATS_PLATFORM = 'own website'

ADVERT_ID = re.compile(r'advertisement_display&(?:amp;)?id=(\d+)')
POSTING_URL = 'https://recrutement.skema.edu/?page=advertisement_display&id='

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, html = lib.fetch_static(CAREERS_LINK, timeout=20)
    if status != 200 or not html:
        raise RuntimeError(f'skema board returned http={status}')
    ids = sorted(set(ADVERT_ID.findall(html)), key=int)
    if not ids:
        raise RuntimeError('skema board listed no adverts')
    return [POSTING_URL + i for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
