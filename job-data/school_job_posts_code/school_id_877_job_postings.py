"""
Job postings scraper for school_id 877 - Rutgers University-New Brunswick (US)
ATS platform: PeopleAdmin (detected: peopleadmin)
Careers link: https://jobs.rutgers.edu/postings/search?query=&query_position_type_id%5B%5D=6&2201%5B%5D=3&commit=Search

Rutgers runs one PeopleAdmin board for the whole university, and three of
our schools sit on it -- Camden, New Brunswick and Newark. The shared
scrape_peopleadmin adapter cannot separate them: it builds its feed URL from
the HOST alone (https://<netloc>/postings/all_jobs.atom), discarding path and
query, so any campus filter placed in the careers link is thrown away and
every school on the host receives an identical 905 postings.

So this school defines its own find_links() instead, which is what the
adapter's docstring recommends for a per-school tweak.

Rutgers' Atom feed carries fields beyond the Atom standard -- school,
divisiondepartment, posting_number -- and "school" names the chancellor's
unit: "New Brunswick Chancellor-L2" (234), "Camden Chancellor's Office-L2"
(64), "Newark Chancellor-L2" (43), "RBHS Chancellor-L2" (514, the biomedical
and health sciences division, which is not one of our schools). Filtering on
that field is exact, so no guessing from prose is involved.

Writes school_job_posts/school_id_877_job_posts.csv (school_id, post_link).
Checkpointed to school_id_877_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
The careers link is a PeopleAdmin search; the search itself is paged so the
link's own filters (position type, campus) are kept -- the board's Atom
feed ignores filters.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 877
SCHOOL_NAME = 'Rutgers University-New Brunswick'
CAREERS_LINK = 'https://jobs.rutgers.edu/postings/search?query=&query_position_type_id%5B%5D=6&2201%5B%5D=3&commit=Search'
ATS_PLATFORM = 'PeopleAdmin'

ATOM = 'https://jobs.rutgers.edu/postings/all_jobs.atom'
# Matched against the feed's own <school> field, not against free text.
CAMPUS = 'New Brunswick'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    return lib.scrape_peopleadmin_search(CAREERS_LINK)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
