"""
Job postings scraper for school_id 1613 - Mount Saint Vincent University (Canada)
ATS platform: own website
Careers link: https://www.msvu.ca/about-msvu/careers-at-the-mount/current-openings/

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Mount Saint Vincent University; nothing here affects any
other school's script.

TUNED FIND_LINKS
Two steps: the full-time and part-time academic pages each embed an
iframe from forms.msvu.ca (FacultyRecruitment/...), and that frame lists
the openings, each .../positiondetail.asp?ID=<id>.

Writes school_job_posts/school_id_1613_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1613_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1613
SCHOOL_NAME = 'Mount Saint Vincent University'
CAREERS_LINK = 'https://www.msvu.ca/about-msvu/careers-at-the-mount/current-openings/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


PAGES = ['https://www.msvu.ca/about-msvu/careers-at-the-mount/current-openings/full-time-academic-positions/',
         'https://www.msvu.ca/about-msvu/careers-at-the-mount/current-openings/part-time-academic-positions/']
FRAME_RE = re.compile(r'<iframe[^>]+src="(https://forms\.msvu\.ca/iframeforms/[^"]+)"', re.I)
POSTING_RE = re.compile(r'^https://forms\.msvu\.ca/iframeforms/FacultyRecruitment/[^?#]+/positiondetail\.asp\?ID=\d+$', re.I)


def find_links():
    import html as _html
    links = []
    for page in PAGES:
        outer = lib._fetch_rendered_retry(page, 4000)
        for frame in FRAME_RE.findall(outer):
            frame = _html.unescape(frame)
            status, inner = lib.fetch_static(frame, timeout=30)
            for url in lib.extract_links(inner or '', frame):
                if POSTING_RE.search(url) and url not in links:
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
