"""
Job info scraper for school_id 1905 - emlyon business school (France)
ATS platform: Workday
Careers link: https://galileo.wd3.myworkdayjobs.com/emlyon_career_site

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if emlyon business school's posting
pages need something the default doesn't handle; nothing here affects any
other school's script.

There is no Workday entry in BULK_ADAPTERS, so each requisition page is
visited individually with the generic detail fetcher. The 48 Workday
requisitions need nothing special.

WHY THE 49TH LINK IS SPECIAL
emlyon's Workday board carries no academic posts at all; its professor
recruitment is a single page (FACULTY_CALL) rather than a board, so the
postings scraper adds that one page as a link. Left to the generic fetcher
it came out titled "FACULTY POSITION" -- the page's <h2> -- and classified
Unclassified, i.e. emlyon showed zero faculty openings even though this page
is one. The rank and the disciplines are not in any heading; they are in the
body sentence, so fetch_detail below lifts them from there and composes a
title out of the page's own words ("Associate / Full professor Levels, in
the areas of Marketing, AI / Digital Technology in Business, Organization
Behavior, and Strategy"). Nothing is invented: if that sentence stops
matching, the composed title is dropped and the generic one is kept.

Note these chairs are at emlyon's SHANGHAI campus while the school is
pinned in Lyon, so the campus is named in the title rather than left to be
inferred from the pin.

Reads posting URLs from school_id_1905_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_1905_job_info.csv. Checkpointed to
school_id_1905_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity. NOTE: a cached entry is never re-fetched, so after
changing the logic below you must purge the affected entries from that
checkpoint or the change has no effect.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo
import job_postings_lib as jlib

SCHOOL_ID = 1905
SCHOOL_NAME = 'emlyon business school'
CAREERS_LINK = 'https://galileo.wd3.myworkdayjobs.com/emlyon_career_site'
ATS_PLATFORM = 'Workday'
USE_LLM = False

FACULTY_CALL = 'https://en.em-lyon.com.cn/research/faculty/recruitment-of-teachers'

# "...seeking faculty candidates at Associate / Full professor Levels, in the
#  areas of Marketing, AI / Digital Technology in Business, Organization
#  Behavior, and Strategy."
SEEKING = re.compile(
    r'seeking\s+faculty\s+candidates\s+at\s+(?P<rank>.{3,60}?)\s+Levels?\s*,\s*'
    r'in\s+the\s+areas\s+of\s+(?P<areas>.{3,200}?)\s*\.',
    re.I | re.S)

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


def _faculty_call_title():
    """Compose the title from the page's own sentence; None if it no longer
    reads the way it did, so we never assert a stale rank or area list."""
    try:
        status, html = jlib.fetch_static(FACULTY_CALL, timeout=25)
    except Exception:
        return None
    if status != 200 or not html:
        return None
    text = re.sub(r'<script.*?</script>', ' ', html, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    match = SEEKING.search(text)
    if not match:
        return None
    rank = match.group('rank').strip()
    areas = match.group('areas').strip()
    return f'Faculty Positions: {rank} in {areas} (Shanghai campus)'


def fetch_detail(url):
    """Contract (job_info_lib.run_school_job_info): return a (title,
    description) 2-tuple, NOT a dict -- the {'title', 'description'} shape
    seen in the checkpoint is what the runner stores afterwards."""
    title, description = jinfo.fetch_detail_generic(url)
    if url == FACULTY_CALL:
        composed = _faculty_call_title()
        if composed:
            return composed, description
    return title, description


def main():
    result = jinfo.run_school_job_info(SCHOOL_ID, JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,
                                       fetch_detail_fn=fetch_detail, use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
