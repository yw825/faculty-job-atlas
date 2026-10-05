"""
Job postings scraper for school_id 1131 - Lehigh University (US)
ATS platform: own website
Careers link: https://facultyjobs.lehigh.edu/faculty

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

WHY THIS WAS REPOINTED
It used to point at careers.pageuppeople.com/865/cw/en-us/listing and run the
generic COMMON_JOB_URL_HINTS filter, which collected 51 links -- 42 PageUp,
8 on hr.lehigh.edu and 1 stray -- of which almost none were jobs. The
hr.lehigh.edu entries were policy pages ("fully-remote-work-policy",
"market-referenced-job-evaluation-process", "benefits/FStuition",
"linkedin-learning-faculty-and-staff"), and on the info side 46 rows came
back with titles like "Main navigation" and "Position Description User
Guides". Only 2 of those 46 classified as professor-grade. Meanwhile
Lehigh's actual faculty board was not being read at all.

THE STRUCTURE IS THREE LEVELS, AND ONLY THE SITEMAP ENUMERATES IT
facultyjobs.lehigh.edu/faculty is an INDEX, not a listing: rendered it is
662 KB and contains zero posting links, only per-college pages. Those
college pages (/all-faculty-openings/college-arts-sciences and friends) are
likewise empty of postings -- 653 KB rendered, no /node/ links, no
Interfolio links, and they do not even name the jobs in their text.
/all-faculty-openings with no college suffix 404s.

sitemap.xml is the only place the postings are enumerated. It lists 20
/node/<id> pages, and each node page is exactly one faculty posting with
its title in <h1> ("Assistant Professor of Organic Chemistry", "Tenure
Track Assistant Professor Cell Biology"). All 20 are faculty-titled.

THE POSTING LINK IS THE NODE PAGE, NOT THE INTERFOLIO URL
19 of the 20 node pages carry an apply.interfolio.com link, so harvesting
those would have been the obvious move. It is the wrong one: node/1296
("Tenure-track Assistant Professor of Accounting") has no Interfolio link
at all and would simply vanish. The node page always exists and always
carries the <h1> title, so it is the stable identifier.

KNOWN LIMITATION, CONFIRMED NOT AN OVERSIGHT
Some Lehigh faculty jobs never appear on this site. apply.interfolio.com/194807
is a genuine Lehigh posting -- rendering it gives h1 "Tenure-Track Assistant
Professor of Industrial and Systems Engineering" and h2 "Lehigh University:
P.C. Rossin College of Engineering & Applied Science" -- yet it is absent
from the sitemap's 20 nodes, from all five college pages, from
engineering.lehigh.edu/ise, and from any Interfolio listing reachable
without JavaScript (Interfolio's search is a JS shell: every URL returns the
same 9,280-byte page). Such postings are reachable only if you already hold
the URL, so this scraper cannot find them and does not pretend to.

Writes school_job_posts/school_id_1131_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1131_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1131
SCHOOL_NAME = 'Lehigh University'
CAREERS_LINK = 'https://facultyjobs.lehigh.edu/faculty'
ATS_PLATFORM = 'own website'

SITEMAP = 'https://facultyjobs.lehigh.edu/sitemap.xml'
NODE_ID = re.compile(r'/node/(\d+)')
POSTING_URL = 'https://facultyjobs.lehigh.edu/node/'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    status, xml = lib.fetch_static(SITEMAP, timeout=20)
    if status != 200 or not xml:
        raise RuntimeError(f'lehigh sitemap returned http={status}')
    ids = sorted(set(NODE_ID.findall(xml)), key=int)
    if not ids:
        raise RuntimeError('lehigh sitemap listed no node pages')
    return [POSTING_URL + i for i in ids]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
