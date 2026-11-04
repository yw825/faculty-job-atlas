"""
Job postings scraper for school_id 1732 - Nova School of Business and Economics (Portugal)
Careers link: https://www.novasbe.unl.pt/en/about-us/join-our-school/faculty-and-researchers

TUNED FIND_LINKS
Nova SBE's "Faculty & Researchers" page (rendered -- the static HTML
lacks the openings) shows the CURRENT openings as announcement PDFs in a
carousel, followed by a "Previous Openings" section of past notices and
their "Definitive List" results. Only PDF links before "Previous Openings"
are collected; the old scraper also took past notices, a 2019 call and
the PhD job-market candidates page.

Writes school_job_posts/school_id_1732_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1732_job_postings.checkpoint next to this script.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1732
SCHOOL_NAME = 'Nova School of Business and Economics'
CAREERS_LINK = 'https://www.novasbe.unl.pt/en/about-us/join-our-school/faculty-and-researchers'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    html = lib._fetch_rendered_retry(CAREERS_LINK, 5000)
    if 'Previous Openings' not in html and 'Faculty' not in html:
        raise RuntimeError('faculty page did not render')
    current = html.split('Previous Openings', 1)[0]
    from urllib.parse import urljoin
    links = []
    for href, label in re.findall(r'<a[^>]+href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', current, re.S | re.I):
        if re.search(r'(?i)definitive|lista|result', label + href):
            continue
        url = urljoin('https://www.novasbe.unl.pt/', href.replace('&amp;', '&'))
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
