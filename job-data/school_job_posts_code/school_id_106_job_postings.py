"""
Job postings scraper for school_id 106 - University of Southern California (US)
ATS platform: own website
Careers link: https://usccareers.usc.edu/category/faculty-jobs/1728-1209/40020/1

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for University of Southern California; nothing here affects any
other school's script.

Link check (ok): 30 posting-shaped links found.

TUNED FIND_LINKS
TalentBrew board. Each posting is /job/<city>/<slug>/<company id>/<job id>.
The board renders 15 results per page, so its own AJAX results endpoint
is paged at 100 per request until a page adds nothing. Only the Faculty
category (40020, ~310 of the board's ~1,050 jobs) is read; the rest of the
board is staff.

Writes school_job_posts/school_id_106_job_posts.csv (school_id, post_link).
Checkpointed to school_id_106_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 106
SCHOOL_NAME = 'University of Southern California'
CAREERS_LINK = 'https://usccareers.usc.edu/category/faculty-jobs/1728-1209/40020/1'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


# Faculty category (id 40020; also exposed as Position Type = Faculty, same
# count). The results XHR only honours it when the facet is passed both as
# the active facet and as an applied FacetFilters entry.
FACULTY_FACET = 40020
RESULTS_API = ('https://usccareers.usc.edu/search-jobs/results?CurrentPage={page}'
               '&RecordsPerPage=100&SearchResultsModuleName=Search+Results'
               '&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0'
               '&SearchType=1&ActiveFacetID={facet}&FacetTerm={facet}&FacetType=1'
               '&CategoryFacetTerm={facet}&CategoryFacetType=1'
               '&FacetFilters%5B0%5D.ID={facet}&FacetFilters%5B0%5D.FacetType=1'
               '&FacetFilters%5B0%5D.Display=Faculty&FacetFilters%5B0%5D.IsApplied=true'
               '&FacetFilters%5B0%5D.FieldName=')
POSTING_RE = re.compile(r'href="(/job/[^"/]+/[^"/]+/\d+/\d+)"')


def find_links():
    import json
    links = []
    for page in range(1, 40):
        status, text = lib.fetch_static(RESULTS_API.format(page=page, facet=FACULTY_FACET), timeout=40,
                                        extra_headers={'X-Requested-With': 'XMLHttpRequest'})
        if status != 200:
            if page == 1:
                raise RuntimeError(f'usc results status={status}')
            break
        found = ['https://usccareers.usc.edu' + p
                 for p in POSTING_RE.findall(json.loads(text).get('results', ''))]
        fresh = [u for u in dict.fromkeys(found) if u not in links]
        if not fresh:
            break
        links.extend(fresh)
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
