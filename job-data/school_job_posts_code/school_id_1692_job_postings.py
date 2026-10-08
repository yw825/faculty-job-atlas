"""
Job postings scraper for school_id 1692 - Ludwig Maximilian University of Munich (Germany)
ATS platform: own website
Careers link: https://www.lmu.de/en/about-lmu/working-at-lmu/job-portal/academic-staff/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Ludwig Maximilian University of Munich; nothing here affects any
other school's script.

TUNED FIND_LINKS
LMU's job lists are a BITE widget (jobs.b-ite.com) fed by a search API,
called here directly with LMU's public widget key. Professorships (01_prof)
and academic staff (02_wiss) are read in BOTH languages -- each language
is a separate posting with its own id, and the example was only in the
English set -- then deduplicated by job number (anr), keeping English.
Each opening is job-portal.lmu.de/jobposting/<id>.

Writes school_job_posts/school_id_1692_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1692_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1692
SCHOOL_NAME = 'Ludwig Maximilian University of Munich'
CAREERS_LINK = 'https://www.lmu.de/en/about-lmu/working-at-lmu/job-portal/academic-staff/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


BITE_SEARCH = 'https://jobs.b-ite.com/api/v1/postings/search'
BITE_KEY = '7d4ebad4ecdfd3e99a89596c85c5e4be21cd9c12'   # LMU's public widget key
ACADEMIC_GROUPS = ['01_prof', '02_wiss']                # professorships, academic staff


def find_links():
    import requests
    headers = {'User-Agent': lib.UA, 'Origin': 'https://www.lmu.de', 'Referer': 'https://www.lmu.de/'}
    by_number = {}
    for locale in ('en', 'de'):                         # English first: it wins a tie
        body = {'key': BITE_KEY, 'channel': 0, 'locale': locale,
                'page': {'offset': 0, 'num': 1000},
                'filter': {'locale': {'in': [locale]},
                           'custom.beschaeftigtengruppe': {'in': ACADEMIC_GROUPS}}}
        r = requests.post(BITE_SEARCH, json=body, headers=headers, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f'lmu bite search status={r.status_code}')
        for post in r.json().get('jobPostings', []):
            by_number.setdefault(post.get('anr') or post['url'], post['url'].split('?')[0])
    return list(by_number.values())


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
