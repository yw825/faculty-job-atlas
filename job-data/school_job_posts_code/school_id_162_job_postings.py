"""
Job postings scraper for school_id 162 - University of Colorado Boulder (US)
ATS platform: own website
Careers link: https://jobs.colorado.edu/jobs/SearchJobs/?6110=13216702&6110_format=2267&listFilterMode=1

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file.

WHY THE GENERIC FILTER WAS REPLACED
This used to render the page and keep anything matching COMMON_JOB_URL_HINTS,
which collected 97 links of which only 25 were jobs. The other 72 were the
board's own furniture and, worse, its social share buttons: 25 facebook.com
and 25 twitter.com links were stored as postings, plus /jobs/living-here,
/jobs/perks, /jobs/frequently-asked-questions, RegisterJobAlert and
RegisterTalentPool. "Living Here" and "Perks" were reaching the published
map as job postings.

The board's real postings all have one shape -- jobs.colorado.edu/jobs/
JobDetail/<slug>/<id> -- so that is matched directly instead.

One subtlety worth keeping: the share buttons embed the posting's own URL in
their query string, e.g.
  http://twitter.com/intent/tweet?url=https%3A%2F%2Fjobs.colorado.edu%2F...
That is percent-encoded, so the literal pattern below does not match it; and
even an unencoded variant would only ever yield the posting URL itself, not
the twitter one. A looser "contains JobDetail" test would have kept them.

The board shows 25 per page ("1-25 of 32") and ignores ?page=N -- which
once made it look unpaginated. It pages with &jobOffset=N, so offsets are
walked in steps of 25 until one adds nothing.

Writes school_job_posts/school_id_162_job_posts.csv (school_id, post_link).
Checkpointed to school_id_162_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 162
SCHOOL_NAME = 'University of Colorado Boulder'
CAREERS_LINK = ('https://jobs.colorado.edu/jobs/SearchJobs/'
                '?6110=13216702&6110_format=2267&listFilterMode=1')
ATS_PLATFORM = 'own website'

MAX_PAGES = 20

POSTING = re.compile(r'https://jobs\.colorado\.edu/jobs/JobDetail/[^"\'?<>\s]+')

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')


def find_links():
    links = []
    for offset in range(0, 25 * MAX_PAGES, 25):
        url = f'{CAREERS_LINK}&jobRecordsPerPage=25&jobOffset={offset}'
        status, html = lib.fetch_static(url, timeout=25)
        if status != 200 or not html:
            html = lib.fetch_rendered(url)
            if lib.is_fetch_failure(html):
                if offset == 0:
                    raise RuntimeError(html)
                break
        fresh = [u for u in dict.fromkeys(POSTING.findall(html)) if u not in links]
        if not fresh:
            break
        links.extend(fresh)
    if not links:
        raise RuntimeError('cu boulder board listed no JobDetail postings')
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
