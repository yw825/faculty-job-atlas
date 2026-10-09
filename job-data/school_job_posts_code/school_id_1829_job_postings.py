"""
Job postings scraper for school_id 1829 - Massey University (New Zealand)
Careers link: https://massey.t1cloud.com/T1Default/CiAnywhere/Web/MASSEY/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES

TUNED FIND_LINKS
Massey's job board is TechnologyOne CiAnywhere. The public entry point
(linked from massey.ac.nz/about/jobs-at-massey) redirects to a
JobBoardEnquiry URL with a per-session G=<guid>; such a URL -- the old
careers link and the one in the audit sheet alike -- later redirects to the
staff LOG ON page, so the public entry point is stored instead. All jobs
(~40) are cards on one rendered page; a job has NO stable URL of its own
(Apply links carry a session hash and the Advertisement panel is disabled
for guests), so each is stored as the public board URL + "#<Reference>"
(e.g. #JR-2417) -- the same scheme as Manitoba/McMaster.

Writes school_job_posts/school_id_1829_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1829_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1829
SCHOOL_NAME = 'Massey University'
CAREERS_LINK = 'https://massey.t1cloud.com/T1Default/CiAnywhere/Web/MASSEY/Public/Function/$ORG.REC.EXJOBB.ENQ/RECRUIT_EXT?suite=CES'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def board_cards():
    """[(reference, title, card text)] for every job card on the board."""
    from bs4 import BeautifulSoup

    def wait_for_cards(page):
        page.wait_for_selector('.thumbnailItem img[alt^="Image for"]', timeout=60000)
        page.wait_for_timeout(2000)
    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=3000, actions=wait_for_cards, timeout=90000)
    if not html or lib.is_fetch_failure(html):
        raise RuntimeError(html or 'board did not render')
    if 'Log On - CiA' in html and 'thumbnailItem' not in html:
        raise RuntimeError('redirected to the staff log-on page')
    out = []
    for card in BeautifulSoup(html, 'html.parser').select('.thumbnailItem'):
        img = card.find('img', alt=re.compile(r'^Image for '))
        ref = card.select_one('.thbFld_JOBREQJobId .editorField')
        if not img or not ref:
            continue
        title = img['alt'][len('Image for '):].strip()
        fields = [d.get('title') or d.get_text(' ', strip=True) for d in card.select('.editorField')]
        out.append((ref.get_text(strip=True), title, ' | '.join(f for f in fields if f)))
    if not out:
        raise RuntimeError('no job cards found')
    return out


def find_links():
    return [f'{CAREERS_LINK}#{ref}' for ref, _title, _text in board_cards()]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
