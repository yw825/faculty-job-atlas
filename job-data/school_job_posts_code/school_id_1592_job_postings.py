"""
Job postings scraper for school_id 1592 - Thompson Rivers University (Canada)
ATS platform: HRSmart
Careers link: https://tru.hua.hrsmart.com/hr/ats/JobSearch/search

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for Thompson Rivers University; nothing here affects any
other school's script.

Starting point (not a tuned answer): fetch the careers page rendered (JS
included), then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If this
under- or over-collects for this school, narrow/widen that pattern, add a
click/scroll step via fetch_rendered's `actions` argument (see
job_postings_lib.scrape_taleo for a real example of clicking through a
search-results page), or follow a department/pagination link with a second
fetch_rendered/fetch_static call and merge the results.

Writes school_job_posts/school_id_1592_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1592_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1592
SCHOOL_NAME = 'Thompson Rivers University'
CAREERS_LINK = 'https://tru.hua.hrsmart.com/hr/ats/JobSearch/search'
ATS_PLATFORM = 'HRSmart'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# A real HRSmart posting is /hr/ats/Posting/view/<id>. The generic
# job-shaped filter also matched the site's own search machinery -- the
# quick/advanced search forms, "view all", "create account", the pagination
# links, and 25 "find similar jobs" lens.php links -- which then appeared as
# 42 postings with a blank title (confirmed live).
POSTING_RE = re.compile(r'/hr/ats/Posting/view/\d+')


PAGE_URL = ('https://tru.hua.hrsmart.com/hr/ats/JobSearch/search/'
            'jobSearchPaginationExternal_page:{page}')


def find_links():
    # 25 postings per page and no "show all" (viewAll returns the same 25),
    # so the pages have to be walked; 139 postings over 6 pages confirmed
    # live. Stops as soon as a page adds nothing new.
    links, seen = [], set()
    for page in range(1, 30):
        html = lib.fetch_rendered(PAGE_URL.format(page=page), wait_ms=3500)
        if lib.is_fetch_failure(html):
            if page == 1:
                raise RuntimeError(html)
            break
        new = [u for u in lib.extract_links(html, CAREERS_LINK, href_pattern=POSTING_RE)
               if u not in seen]
        if not new:
            break
        seen.update(new)
        links.extend(new)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
