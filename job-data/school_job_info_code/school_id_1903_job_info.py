"""
Job info scraper for school_id 1903 - EDHEC Business School (France)
ATS platform: own website
Careers link: https://www.edhec.edu/en/jobs

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if EDHEC Business School's posting
pages need something the default doesn't handle; nothing here affects any
other school's script.

EDHEC's posting pages embed schema.org JobPosting JSON-LD (title,
employmentType, datePosted, validThrough) alongside the visible text.

WHY THIS SCHOOL OVERRIDES THE TITLE
The generic fetcher's title cleaner (job_info_lib._title_candidates_from_text)
splits on ' - ', ' – ' and ' — ' and keeps the LEFT side, because WordPress
job boards append the site name after an en-dash ("Decano(a) Auxiliar –
Universidad Interamericana de Puerto Rico"). That rule is right for most
schools and wrong for this one: EDHEC separates the RANK from the
DISCIPLINE with the same en-dash, so "Assistant, Associate, or Full
Professor – Geopolitics" was being stored as "Assistant, Associate, or Full
Professor". Eight of nineteen postings collapsed onto two indistinguishable
titles -- geopolitics, humanities, human resources, business ethics,
organizational behavior (x2), political sciences and quantitative marketing
were all unreadable on the map.

The fix is local, not a library change: the shared splitter still serves the
other ~1540 schools. Here the untruncated title is taken straight from the
page's own JSON-LD (falling back to og:title, which also carries no site
suffix), and only when it is richer than what the generic pass produced.

Reads posting URLs from school_id_1903_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_1903_job_info.csv. Checkpointed to
school_id_1903_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity. NOTE: a cached entry is never re-fetched, so after
changing the logic below you must purge this school's entries from that
checkpoint or the change has no effect.
"""
import html as htmllib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo
import job_postings_lib as jlib

SCHOOL_ID = 1903
SCHOOL_NAME = 'EDHEC Business School'
CAREERS_LINK = 'https://www.edhec.edu/en/jobs'
ATS_PLATFORM = 'own website'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

# "@type":"JobPosting", ... "title":"Assistant, Associate, or Full Professor – Geopolitics"
JSONLD_TITLE = re.compile(
    r'"@type"\s*:\s*"JobPosting".{0,400}?"title"\s*:\s*"((?:[^"\\]|\\.)*)"', re.S)
OG_TITLE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)


def _decode(raw):
    """JSON-LD escapes solidus and non-ASCII (\\/ and \\u2013); decode as a
    JSON string, then unescape any HTML entities that survived into it."""
    try:
        raw = json.loads('"' + raw + '"')
    except ValueError:
        raw = raw.replace('\\/', '/')
    return htmllib.unescape(raw).strip()


def fetch_detail(url):
    """Contract (job_info_lib.run_school_job_info): return a (title,
    description) 2-tuple, NOT a dict -- the {'title', 'description'} shape
    seen in the checkpoint is what the runner stores afterwards."""
    title, description = jinfo.fetch_detail_generic(url)
    try:
        status, html = jlib.fetch_static(url, timeout=20)
    except Exception:
        return title, description  # keep the generic result, don't lose the row
    if status != 200 or not html:
        return title, description
    match = JSONLD_TITLE.search(html) or OG_TITLE.search(html)
    if not match:
        return title, description
    full = _decode(match.group(1))
    # only when it actually says more -- never shorten a good generic title
    if full and len(full) > len(title or ''):
        return full, description
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
