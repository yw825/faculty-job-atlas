"""
Job postings scraper for school_id 489 - Centre College (US)
ATS platform: Workday
Careers link: https://centrecollege.wd501.myworkdayjobs.com/Centre

Uses the shared Workday adapter (job_postings_lib.scrape_workday) against
BOTH of this school's Workday sites.

WHY THIS WAS REPOINTED
It used to point at https://careers.centre.edu/channels/search-for-a-job/,
which is not a job board at all: careers.centre.edu is Centre's uConnect
career-ADVICE site, whose links are /channels/<topic>/, /account/signup/ and
/resources/. Not one of the 80 links the old generic filter collected was a
job; 20 of them were social share buttons (facebook 7, linkedin 6, twitter 6,
instagram 1). The real board is Centre's own Workday tenant, linked from
www.centre.edu/about/employment-centre.

Centre publishes two Workday sites and both are read here:
  /Centre    the staff board -- 7 postings
  /CentreF   the faculty board -- currently EMPTY of real jobs

THE ONE FACULTY RECORD IS NOT A JOB
/CentreF's single entry is titled "New Test for Faculty - Do NOT Apply"
(JR100243) -- a test record the school left published, telling readers in
the title itself not to apply. NOT_A_POSTING drops it, because publishing it
would put a fake faculty opening on the map at a school that has none. If
Centre later posts real faculty jobs they will come through this same site
untouched; only the explicit test record is excluded.

So the honest current total is 7, all staff (Public Safety Officer,
Custodian, Life Sciences Technician and similar). The tenant is
`centrecollege` and every location is Danville, Kentucky -- Centre's own
campus -- so there is no group-tenant pooling risk here.

Writes school_job_posts/school_id_489_job_posts.csv (school_id, post_link).
Checkpointed to school_id_489_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 489
SCHOOL_NAME = 'Centre College'
CAREERS_LINK = 'https://centrecollege.wd501.myworkdayjobs.com/Centre'
FACULTY_SITE = 'https://centrecollege.wd501.myworkdayjobs.com/CentreF'
ATS_PLATFORM = 'Workday'

# a published test record that says so in its own title
NOT_A_POSTING = re.compile(r'Do-NOT-Apply|New-Test-for-Faculty', re.I)

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = set()
    failures = []
    for site in (CAREERS_LINK, FACULTY_SITE):
        try:
            links |= set(lib.scrape_workday(site, school_name=SCHOOL_NAME))
        except Exception as exc:
            # one site being down must not lose the other's postings
            failures.append(f'{site.rsplit("/", 1)[1]}: {type(exc).__name__}')
    links = {l for l in links if not NOT_A_POSTING.search(l)}
    if not links:
        detail = ' -- ' + '; '.join(failures) if failures else ''
        raise RuntimeError('centre workday sites listed no real postings' + detail)
    return sorted(links)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
