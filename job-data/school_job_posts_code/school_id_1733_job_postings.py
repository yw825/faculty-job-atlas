"""
Job postings scraper for school_id 1733 - Universidade de Coimbra (Portugal)
Careers link: https://www.apply.uc.pt/

TUNED FIND_LINKS
The university's own call platform, UC Apply (apply.uc.pt), where every
Coimbra recruitment procedure is published. Its search results come from a
JSON service (applynext.fw.uc.pt/v1/search, see lib.uc_apply_calls); the
types read are professors (Docentes) and researchers (Investigadores, incl.
DL 57/2016 contracts) -- not research grants, technical staff or managers.
A call is kept until its applications_end date has passed (calls published
but not yet open, "Candidaturas iniciam a ...", are kept). Each call's page
is https://www.apply.uc.pt/procedure/<key>. The old link was the open-
positions page of ADAI, a research association, not the university.

Writes school_job_posts/school_id_1733_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1733_job_postings.checkpoint next to this script.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1733
SCHOOL_NAME = 'Universidade de Coimbra'
CAREERS_LINK = 'https://www.apply.uc.pt/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    today = datetime.date.today().isoformat()
    return [f'https://www.apply.uc.pt/procedure/{key}'
            for key, rec in lib.uc_apply_calls().items()
            if (rec.get('applications_end') or '') >= today]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
