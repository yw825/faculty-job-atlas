"""
Job postings scraper for school_id 1664 - KU Leuven (Belgium)
ATS platform: own website
Careers link: https://www.kuleuven.be/personeel/jobsite/jobs/professor?lang=nl

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for KU Leuven; nothing here affects any
other school's script.

TUNED FIND_LINKS
The professor list is a web component fed by a search API
(icts-p-fii-toep-component-filter2.../api/projects/Jobsite_professor/search),
which is called directly; each hit's id becomes the posting URL
www.kuleuven.be/personeel/jobsite/jobs/<id>.

Writes school_job_posts/school_id_1664_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1664_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1664
SCHOOL_NAME = 'KU Leuven'
CAREERS_LINK = 'https://www.kuleuven.be/personeel/jobsite/jobs/professor?lang=nl'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


SEARCH_API = ('https://icts-p-fii-toep-component-filter2.cloud.icts.kuleuven.be/'
              'api/projects/Jobsite_professor/search?lang=nl&page={page}')
POSTING_URL = 'https://www.kuleuven.be/personeel/jobsite/jobs/{}'


def find_links():
    import json
    links, total = [], None
    for page in range(0, 30):          # 0-based; page=1 is the SECOND page
        status, text = lib.fetch_static(SEARCH_API.format(page=page), method='POST', timeout=30,
                                        json_body={'_locale': 'nl', 'environment': 'production', 'release': ''})
        if status != 200:
            raise RuntimeError(f'kuleuven search api status={status}')
        data = json.loads(text)
        total = data.get('total_nb_hits', total)
        hits = data.get('hits') or []
        fresh = [POSTING_URL.format(h['_id']) for h in hits if POSTING_URL.format(h['_id']) not in links]
        if not fresh:
            break
        links.extend(fresh)
        if total is not None and len(links) >= total:
            break
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
