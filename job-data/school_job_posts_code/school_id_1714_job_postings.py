"""
Job postings scraper for school_id 1714 - Politecnico di Torino (Italy)
ATS platform: own website
Careers link: https://careers.polito.it/default.aspx?qualificaAggr=DO

PARTIALLY CUSTOMIZED (confirmed live, not fully solved): this is a
DevExpress ASPX app. Every listed posting is a plain
`javascript:btnSelezioneClick('<ref>')` handler with no real href at all --
but the ref code itself (e.g. "85/26/IR") is right there in the onclick
text, so it's read directly rather than clicked. Confirmed live: the
`qualificaAggr=DO` filter in CAREERS_LINK currently matches nothing
("Nessun risultato trovato con il filtro selezionato") and the app falls
back to showing ALL 19 open postings across every category, unfiltered --
so this may currently return more than what "DO" alone would once that
category has real openings again.

NOT solved: only the first 10 of those 19 postings render by default; the
rest sit behind a "Visualizza altri dati" (show more) button that would
not click through in this session -- clicks landed on the loading overlay
regardless of a normal click, force click, or a JS-dispatched click.
Whoever picks this up next should try intercepting the underlying
DevExpress callback request instead of clicking the button.

Writes school_job_posts/school_id_1714_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1714_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1714
SCHOOL_NAME = 'Politecnico di Torino'
CAREERS_LINK = 'https://careers.polito.it/default.aspx?qualificaAggr=DO'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

SELEZIONE_RE = re.compile(r"btnSelezioneClick\('([^']+)'\)")


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    refs = SELEZIONE_RE.findall(html)
    seen, links = set(), []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            links.append(f'{CAREERS_LINK}#selezione={ref.replace("/", "-")}')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
