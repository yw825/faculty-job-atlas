"""
Job postings scraper for school_id 1634 - York University (Canada)
ATS platform: own website
Careers link: https://www.yorku.ca/unit/vpf/full-time-faculty-positions/

CUSTOMIZED (confirmed live): postings are listed inside a "All Available
Faculty Positions" accordion, one section per faculty/school. The links are
already present in the raw DOM at page load (the accordion only toggles CSS
visibility, doesn't inject content on click), but the generic default's
job-shaped filter misses them -- each posting is a link straight to a PDF
(e.g. ".../wp-content/uploads/sites/698/2026/08/HUMA.LAPS_IndStud.pdf")
whose href has no job-shaped keyword in it at all, and whose link text is a
plain rank+title ("Assistant Professor - Indigenous Women and Cultures of
Resistance") with no "job/career/posting" word either. Broadening the
site-wide default to catch "Professor"/"Faculty" would flood every other
school's default with nav noise (this page alone has "Faculty & Staff",
"Faculty Affairs", "Faculty Recruitment" as unrelated nav links), so this is
scoped to just the accordion's own content area instead: every link inside
a kt-accordion-panel-inner block, excluding the ">>Visit the X website"
per-faculty nav links that live in the same panels.

TUNED FIND_LINKS
Each opening is a PDF ad under /unit/vpf/wp-content/uploads/, linked from
the full-time faculty positions page.

Writes school_job_posts/school_id_1634_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1634_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1634
SCHOOL_NAME = 'York University'
CAREERS_LINK = 'https://www.yorku.ca/unit/vpf/full-time-faculty-positions/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


POSTING_RE = re.compile(r'^https://www\.yorku\.ca/unit/vpf/wp-content/uploads/[^?#]+\.pdf$', re.I)


def find_links():
    return lib.scrape_matching(CAREERS_LINK, POSTING_RE)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
