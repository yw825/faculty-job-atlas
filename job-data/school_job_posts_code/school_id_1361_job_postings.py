"""
Job postings scraper for school_id 1361 - McMurry University (US)
ATS platform: BambooHR
Careers link: https://mcmurry.bamboohr.com/careers

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.
detect_platform does not know BambooHR and only this one school in
schools_master uses it, so the logic lives here rather than in the library.

The careers link was https://oncampusdining.com/mcm/job-opportunities/ --
the site of the university's FOOD SERVICE contractor, listing its dining
vacancies rather than McMurry's own hiring.

McMurry's careers page embeds BambooHR via a script tag, so the openings are
never in that page's HTML. BambooHR publishes them as JSON at
/careers/list, which needs no auth: 17 postings, "Adjunct Faculty Pool" and
"Dual Credit Adjunct" among them, each addressable at /careers/<id>.

Writes school_job_posts/school_id_1361_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1361_job_postings.checkpoint next to this script.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1361
SCHOOL_NAME = 'McMurry University'
CAREERS_LINK = 'https://mcmurry.bamboohr.com/careers'
ATS_PLATFORM = 'BambooHR'

LIST_API = 'https://mcmurry.bamboohr.com/careers/list'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, text = lib.fetch_static(LIST_API,
                                    extra_headers={'Accept': 'application/json'})
    if status != 200 or not text:
        raise RuntimeError(f'bamboohr careers list status={status}')
    try:
        data = json.loads(text)
    except ValueError as e:
        raise RuntimeError(f'bamboohr careers list not json: {e}')
    links, seen = [], set()
    for row in (data.get('result') or []):
        jid = row.get('id')
        if jid is None:
            continue
        url = f'{CAREERS_LINK}/{jid}'
        if url not in seen:
            seen.add(url)
            links.append(url)
    if not links:
        raise RuntimeError('bamboohr careers list returned no postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
