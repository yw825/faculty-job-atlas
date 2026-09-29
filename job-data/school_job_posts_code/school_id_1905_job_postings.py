"""
Job postings scraper for school_id 1905 - emlyon business school (France)
ATS platform: Workday
Careers link: https://galileo.wd3.myworkdayjobs.com/emlyon_career_site

Uses the shared Workday adapter (job_postings_lib.scrape_workday), plus one
hand-added link explained below.

The tenant `galileo` is the Galileo Global Education group, which owns
several schools -- so a group tenant would normally be a pooling risk, the
same trap that put one board's jobs under three schools elsewhere in this
set. It is safe here because the site path `emlyon_career_site` is already
emlyon's own: all 48 requisitions it returns are located in Lyon (45),
Paris (2) and one multi-location, i.e. emlyon's own campuses, with no other
Galileo school's postings mixed in. Verified before this school was added.

The Workday board carries NO academic posts -- all 48 are administrative and
pedagogical-support roles. emlyon's actual professor recruitment is not on a
board at all: FACULTY_CALL below is a single page advertising open
Associate/Full Professor searches in Marketing, AI/Digital Technology in
Business, Organizational Behavior and Strategy, applied for by emailing
faculty-recruitment1@em-lyon.com.cn. There are no per-posting URLs to
harvest from it, so the page itself is added as one link; the info stage
reads its title and description like any other posting.

Two caveats on that link, both deliberate:
  * those chairs are at emlyon's SHANGHAI campus, while this school is
    pinned in Lyon. It is genuinely emlyon, but the posting is not in France.
  * the en.em-lyon.com.cn host is slow and intermittently times out under
    Playwright, so it is fetched statically and added only on success --
    a failure there must not lose the 48 Workday requisitions.

Writes school_job_posts/school_id_1905_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1905_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1905
SCHOOL_NAME = 'emlyon business school'
CAREERS_LINK = 'https://galileo.wd3.myworkdayjobs.com/emlyon_career_site'
ATS_PLATFORM = 'Workday'

FACULTY_CALL = 'https://en.em-lyon.com.cn/research/faculty/recruitment-of-teachers'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = set(lib.scrape_workday(CAREERS_LINK, school_name=SCHOOL_NAME))
    try:
        status, html = lib.fetch_static(FACULTY_CALL, timeout=25)
        if status == 200 and html:
            links.add(FACULTY_CALL)
        else:
            print(f'  note: faculty call page returned http={status}, skipped')
    except Exception as exc:  # never lose the Workday requisitions over this
        print(f'  note: faculty call page unreachable ({type(exc).__name__}), skipped')
    return sorted(links)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
