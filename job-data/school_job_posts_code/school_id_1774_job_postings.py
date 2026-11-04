"""
Job postings scraper for school_id 1774 - University College London (United Kingdom)
ATS platform: own website (TalentLink widget embedded directly in the page)

CUSTOMIZED (confirmed live): this page is NOT actually blocked by anything --
it just needs its cookie-consent banner ("Accept all cookies") clicked before
the embedded TalentLink vacancy widget renders. There is no iframe involved
(unlike icims/IE University) -- the widget renders inline in the top document
once the banner is dismissed. After accepting cookies, the results list is
already populated (no need to click "Search" separately, but doing so is
harmless and used here for robustness). "Show more results" is a
load-more button; clicked repeatedly until it disappears or stops adding
new jobIds. Confirmed live: 12 unique jobId postings on one run.

Posting URLs are of the form:
  https://www.ucl.ac.uk/work-at-ucl/search-ucl-jobs/details?jobId=<id>&jobTitle=<title>

Writes school_job_posts/school_id_1774_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1774_job_postings.checkpoint next to this script.

TUNED FIND_LINKS
UCL's job search page is a Lumesse TalentLink widget behind a bot wall
(the bundled browser gets a block page); the widget's own data service is
read with its public guest login (lib.talentlink_jobs). A posting is the
search page's details URL with ?jobId=<id> (the jobTitle parameter in the
audit's example is decorative).
UCL School of Management faculty posts on Interfolio are added.
"""
import os
import re
import sys
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1774
SCHOOL_NAME = 'University College London'
CAREERS_LINK = 'https://www.ucl.ac.uk/work-at-ucl/search-ucl-jobs'
ATS_PLATFORM = 'own website'

TALENTLINK = ('emea5-foc.lumessetalentlink.com', 'Q1KFK026203F3VBQBLO8M8M07', '52', 'https://www.ucl.ac.uk/')
JOB_URL = 'https://www.ucl.ac.uk/work-at-ucl/search-ucl-jobs/details?jobId={id}'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

JOB_ID_RE = re.compile(r'href="([^"]*details\?jobId=\d+[^"]*)"')


def find_links():
    links = [JOB_URL.format(id=job['id']) for job in lib.talentlink_jobs(*TALENTLINK)]
    try:  # the School of Management posts its faculty jobs on Interfolio (board 21805)
        links += lib.scrape_interfolio('https://apply.interfolio.com/21805/positions')
    except RuntimeError:
        pass
    return links


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
