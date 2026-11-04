"""
Job postings scraper for school_id 1902 - SKEMA Business School (France)
ATS platform: own website
Careers link: https://recrutement.skema.edu/?page=advertisement

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

SKEMA runs its own small PHP recruiting board (eRecruiting). The listing is
in the static HTML (~15 KB, no JS), so this fetches statically rather than
paying for a render. Each advert is linked as `?page=advertisement_display&id=N`,
so the ids are harvested and rebuilt into canonical URLs -- the raw hrefs
come back HTML-escaped (`&amp;id=`), which is why the pattern tolerates the
entity but the emitted link never contains it.

THE BOARD PAGINATES, 10 PER PAGE. This was missed on the first pass and the
school went in with half its jobs: the page footer reads "1 - 10 / 20" and
the pager is a JS hop, `function goto(id){ location="?page=advertisement&sort=&p="+id; }`,
so there is no ordinary rel=next link to follow. Walking `&sort=&p=N` gives
20 adverts, not 10.

The stop condition is "a page contributed no id an earlier page didn't
already have", NOT an HTTP error and NOT an empty page: p=3 past the end
still returns 200 and in fact echoes every id back (its counter reads a
nonsensical "21 - 20 / 20"), so any other rule either loops or stops early.

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
LIST_PAGE = 'https://recrutement.skema.edu/?page=advertisement&sort=&p='
MAX_PAGES = 20  # safety net; the loop normally stops on its own

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    seen = set()
    for page in range(1, MAX_PAGES + 1):
        status, html = lib.fetch_static(LIST_PAGE + str(page), timeout=20)
        if status != 200 or not html:
            if page == 1:
                raise RuntimeError(f'skema board page 1 returned http={status}')
            break
        ids = set(ADVERT_ID.findall(html))
        # a page past the end re-serves ids we already have, so "nothing new"
        # is the end of the board
        if page > 1 and not ids - seen:
            break
        seen |= ids
    if not seen:
        raise RuntimeError('skema board listed no adverts')
    return [POSTING_URL + i for i in sorted(seen, key=int)]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
