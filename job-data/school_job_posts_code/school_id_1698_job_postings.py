"""
Job postings scraper for school_id 1698 - Corvinus University of Budapest (Hungary)
ATS platform: own website
Careers link: https://www.uni-corvinus.hu/ind/career-opportunities-at-corvinus/career-in-academia/?lang=en

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Corvinus University of Budapest; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps: Career in Academia links each institute's open-calls page
(.../career-in-academia/<institute>/open-calls/, or nyilvanos-palyazatok),
and those link each call, /main-page/about-the-university/institutes/
<institute>/<call>/?lang=en.

Writes school_job_posts/school_id_1698_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1698_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1698
SCHOOL_NAME = 'Corvinus University of Budapest'
CAREERS_LINK = 'https://www.uni-corvinus.hu/ind/career-opportunities-at-corvinus/career-in-academia/?lang=en'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


HUB_RE = re.compile(r'^https://www\.uni-corvinus\.hu/ind/career-opportunities-at-corvinus/career-in-academia/'
                    r'[^/?#]+/(?:open-calls|nyilvanos-palyazatok)/\?lang=en$', re.I)
POSTING_RE = re.compile(r'^https://www\.uni-corvinus\.hu/main-page/about-the-university/institutes/[^/?#]+/[^/?#]+/\?lang=en$', re.I)


def find_links():
    return lib.scrape_two_hop(CAREERS_LINK, HUB_RE, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
