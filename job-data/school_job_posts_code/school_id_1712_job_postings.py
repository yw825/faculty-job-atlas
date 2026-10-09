"""
Job postings scraper for school_id 1712 - LUISS Guido Carli (Italy)
Source: bandi.mur.gov.it (Ministero dell'Universita e della Ricerca)
Careers link: https://bandi.mur.gov.it/profcalls.php/public/cercaJobs?jv_comp_status_id=2-3&bb_type_code=LUISS&idsettore=%25&idgsd24=%25&idqualifica=%25&azione=cerca

TUNED FIND_LINKS
Italian universities must publish their professor calls (chiamata dei
professori, prima/seconda fascia) and fixed-term / tenure-track researcher
calls (ricercatori a tempo determinato) on the Ministry's national portal.
This school's open calls are read there by its portal code (LUISS); each
call is bandi.mur.gov.it/<profcalls|jobs>.php/public/job/id_job/<id>. The
university's own pages were replaced on 2026-10-09 because they were not
job boards (Bocconi's linked its PhD job-market candidates; Bologna's only
teaching contracts; Padua's whole official notice board). Teaching
contracts, research contracts and research grants are deliberately not
collected.

Writes school_job_posts/school_id_1712_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1712_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1712
SCHOOL_NAME = 'LUISS Guido Carli'
CAREERS_LINK = 'https://bandi.mur.gov.it/profcalls.php/public/cercaJobs?jv_comp_status_id=2-3&bb_type_code=LUISS&idsettore=%25&idgsd24=%25&idqualifica=%25&azione=cerca'
ATS_PLATFORM = 'MUR bandi (national portal)'
MUR_CODE = 'LUISS'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_mur(MUR_CODE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
