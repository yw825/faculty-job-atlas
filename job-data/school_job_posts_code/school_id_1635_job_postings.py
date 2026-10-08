"""
Job postings scraper for school_id 1635 - University of Waterloo (Canada)
ATS platform: own website
Careers link: https://uwaterloo.ca/careers/current-opportunities/faculty-opportunities

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Waterloo; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps, two sources. The faculty-opportunities page links each
faculty's own openings page (Arts, Health, Engineering, Math, Environment,
Science); those link PDF ads (/<faculty>/sites/default/files/...pdf) or,
in Engineering, an ad page. Several units instead post on Waterloo's Online
Faculty Application System, whose home page lists the hiring units and
each unit its jobs (ofas.uwaterloo.ca/job-details/<id>); both are merged.

Writes school_job_posts/school_id_1635_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1635_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1635
SCHOOL_NAME = 'University of Waterloo'
CAREERS_LINK = 'https://uwaterloo.ca/careers/current-opportunities/faculty-opportunities'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


HUB_RE = re.compile(r'^https://uwaterloo\.ca/(?!careers/)[^/?#]+/(?:[^?#]*/)?'
                    r'(?:faculty-positions-available|employment|faculty-openings|'
                    r'employment-opportunities)$', re.I)
POSTING_RE = re.compile(r'^https://(?:uwaterloo\.ca/[^/?#]+/sites/default/files/[^?#]+\.pdf'
                        r'|uwaterloo\.ca/engineering/(?:faculty-opening|full-professor)[^/?#]*'
                        r'|ofas\.uwaterloo\.ca/job-details/\d+)$', re.I)
OFAS_HOME = 'https://ofas.uwaterloo.ca/'
OFAS_UNIT_RE = re.compile(r'^https://ofas\.uwaterloo\.ca/available-positions-in/[^/?#]+$', re.I)


def find_links():
    links = lib.scrape_two_hop(CAREERS_LINK, HUB_RE, POSTING_RE)
    for url in lib.scrape_two_hop(OFAS_HOME, OFAS_UNIT_RE, POSTING_RE):
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
