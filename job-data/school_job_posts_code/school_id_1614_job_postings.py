"""
Job postings scraper for school_id 1614 - NSCAD University (Canada)
ATS platform: own website
Careers link: https://nscad.ca/careers/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for NSCAD University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Openings come from a CareerBeacon widget (jobs.careerbeacon.com/details/
<slug>/<id>, stored without its utm_* tracking), plus PDF vacancy notices
under /wp-content/uploads/. The "apply" links
beside each are not stored. The widget is built client-side, so the page is
rendered.

Writes school_job_posts/school_id_1614_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1614_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1614
SCHOOL_NAME = 'NSCAD University'
CAREERS_LINK = 'https://nscad.ca/careers/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


OWN_RE = re.compile(r'^https://nscad\.ca/wp-content/uploads/[^?#]+\.pdf$', re.I)
CAREERBEACON_RE = re.compile(r'^https://jobs\.careerbeacon\.com/details/[^/?#]+/\d+', re.I)


def find_links():
    links = []
    for url in lib.scrape_matching(CAREERS_LINK, re.compile(OWN_RE.pattern + '|' + CAREERBEACON_RE.pattern, re.I),
                                   render=True):
        # the widget's links carry utm_* tracking that differs per widget
        # source; the bare details URL is the posting
        url = CAREERBEACON_RE.match(url).group(0) if CAREERBEACON_RE.match(url) else url
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
