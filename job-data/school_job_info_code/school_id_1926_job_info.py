"""
Job info scraper for school_id 1926 - University of Massachusetts-Chan Medical School (US)
ATS platform: AcademicJobsOnline
Careers link: https://academicjobsonline.org/ajo/UMASSMED

Reads posting URLs from school_id_1926_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

Writes school_job_info/school_id_1926_job_info.csv. Checkpointed to
school_id_1926_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1926
SCHOOL_NAME = 'University of Massachusetts-Chan Medical School'
CAREERS_LINK = 'https://academicjobsonline.org/ajo/UMASSMED'
ATS_PLATFORM = 'AcademicJobsOnline'
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')

def fetch_detail(url):
    """AcademicJobsOnline advert; title = "Position Title" + the department named in the heading."""
    title, text = jinfo.fetch_detail_academicjobsonline(url)
    head = re.match(r'\s*(.{3,200}?)\s+Skip to main content', text)
    unit = re.sub(r',?\s*University of Massachusetts Chan Medical School,?\s*', ' ', head.group(1)).strip(' ,') if head else ''
    m = re.search(r'Position Title:\s*(.{3,150}?)\s+Position Type:', text)
    if m:
        title = m.group(1) + (f' - {unit}' if unit and unit.lower() not in m.group(1).lower() else '')
    return title, text


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
