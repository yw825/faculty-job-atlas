"""
Job postings scraper for school_id 1658 - TU Wien (Austria)
ATS platform: own website
Careers link: https://jobs.tuwien.ac.at/jobs?jobProfiles=Associate%20Professor_in|Laufbahnstelle|Professuren|Rektor_in

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for TU Wien; nothing here affects any
other school's script.

TUNED FIND_LINKS
Each opening is jobs.tuwien.ac.at/Job/<id>; the list is built
client-side, so pages are rendered. The professor-profile filter in this
link was empty on 2026-10-08 (per the audit note) while academic posts --
the example is a PraeDoc university assistant -- sit under the
scientific-staff profiles, so both filters are read.

Writes school_job_posts/school_id_1658_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1658_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1658
SCHOOL_NAME = 'TU Wien'
CAREERS_LINK = 'https://jobs.tuwien.ac.at/jobs?jobProfiles=Associate%20Professor_in|Laufbahnstelle|Professuren|Rektor_in'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://jobs\.tuwien\.ac\.at/Job/\d+$', re.I)
# The professor profiles (this link) are usually empty; academic hiring is
# mostly under the scientific-staff profiles (PraeDoc/PostDoc assistants,
# Senior Lecturer/Scientist, doctoral college), which are read as well.
SCIENTIFIC_STAFF = ('https://jobs.tuwien.ac.at/jobs?jobProfiles=Doktoratskolleg|Senior%20Lecturer|'
                    'Senior%20Scientist|Universit%C3%A4tsassistent_in%20PraeDoc|'
                    'Universit%C3%A4tsassistent_in%20PostDoc')


def find_links():
    links = []
    for listing in (CAREERS_LINK, SCIENTIFIC_STAFF):
        for url in lib.scrape_matching(listing, POSTING_RE, render=True):
            if url not in links:
                links.append(url)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
