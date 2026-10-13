"""
Job info scraper for school_id 340 - Maharishi International University (US)
ATS platform: own website
Careers link: https://services.miu.edu/human-resources/faculty/

Reads posting URLs from school_id_340_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.


area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_340_job_info.csv. Checkpointed to
school_id_340_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 340
SCHOOL_NAME = 'Maharishi International University'
CAREERS_LINK = 'https://services.miu.edu/human-resources/faculty/'
ATS_PLATFORM = 'own website'
USE_LLM = False

POSITIONS_PAGE = 'https://services.miu.edu/human-resources/faculty/faculty-positions-available/'


def positions():
    """[(slug, title, text)] -- every advert on the page opens "POSITION TITLE:"."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(jinfo.jlib._fetch_rendered_retry(POSITIONS_PAGE, 5000), 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    text = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
    out = []
    for block in re.split(r'(?=POSITION TITLE:)', text)[1:]:
        m = re.match(r'POSITION TITLE:\s*(.+?)\s+(?:DUTIES|REQUIREMENTS|QUALIFICATIONS|DEPARTMENT|LOCATION)\b', block)
        title = (m.group(1) if m else block[15:95]).strip(' :-')
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80] or 'position'
        if slug in [s for s, _t, _b in out]:
            slug = f'{slug}-{len(out) + 1}'
        out.append((slug, title, block[:20000]))
    return out

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    slug = url.partition('#')[2]
    for s, title, text in positions():
        if s == slug:
            return title[:250], text
    raise RuntimeError('position no longer on the page')


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
