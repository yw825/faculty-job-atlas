"""
Job postings scraper for school_id 880 - Rutgers University-Newark (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.rutgers.edu/postings/search

The careers link was
careers.newark.rutgers.edu/channels/detecting-fraudulent-job-postings/ --
a career-services ADVICE ARTICLE about spotting fraudulent job adverts. It
is on a careers host and full of the word "job", so the generic filter
harvested 84 links from it and none of them was a posting.

Rutgers runs one PeopleAdmin board for the whole university, and three of
our schools sit on it -- Newark, Camden and New Brunswick. The shared
scrape_peopleadmin adapter cannot separate them: it builds its feed URL from
the HOST alone (https://<netloc>/postings/all_jobs.atom), discarding path and
query, so any campus filter placed in the careers link is thrown away and
every school on the host receives an identical 905 postings.

So this school defines its own find_links() instead, which is what the
adapter's docstring recommends for a per-school tweak.

Rutgers' Atom feed carries fields beyond the Atom standard -- school,
divisiondepartment, posting_number -- and "school" names the chancellor's
unit: "Newark Chancellor-L2" (43), "Camden Chancellor's Office-L2" (64),
"New Brunswick Chancellor-L2" (234), "RBHS Chancellor-L2" (514, the
biomedical and health sciences division, which is not one of our schools).
Filtering on that field is exact, so no guessing from prose is involved.

Writes school_job_posts/school_id_880_job_posts.csv (school_id, post_link).
Checkpointed to school_id_880_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 880
SCHOOL_NAME = 'Rutgers University-Newark'
CAREERS_LINK = 'https://jobs.rutgers.edu/postings/search'
ATS_PLATFORM = 'PeopleAdmin'

ATOM = 'https://jobs.rutgers.edu/postings/all_jobs.atom'
# Matched against the feed's own <school> field, not against free text.
CAMPUS = 'Newark'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    from bs4 import BeautifulSoup
    status, text = lib.fetch_static(ATOM)
    if status != 200 or not text:
        raise RuntimeError(f'rutgers atom status={status}')
    soup = BeautifulSoup(text, 'xml')
    links, seen = [], set()
    for entry in soup.find_all('entry'):
        school = entry.find('school')
        if not school or CAMPUS.lower() not in school.get_text().lower():
            continue
        link = entry.find('link')
        href = link.get('href') if link is not None and link.has_attr('href') else None
        if href and href not in seen:
            seen.add(href)
            links.append(href)
    if not links:
        raise RuntimeError(f'no rutgers postings whose school names {CAMPUS!r}')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
