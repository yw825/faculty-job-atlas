"""
Generates the per-school scraper pair for every school in a country:

    school_job_posts_code/school_id_<id>_job_postings.py
    school_job_info_code/school_id_<id>_job_info.py

Run from job-data/:
    python3 generate_school_scripts.py US
    python3 generate_school_scripts.py US --only-verified   # skip broken links
    python3 generate_school_scripts.py US --force           # overwrite edits

EVERY SCHOOL GETS ITS OWN FILE, including schools that share an ATS with
dozens of others. That is the point of the layout: a school whose results
need a tweak gets it in its own file, and no other school is touched. A
platform school's file is thin -- it calls the shared adapter -- but it is
still the place to override find_links() for that one school when the
shared adapter is right for everyone else.

Existing files are NEVER overwritten without --force. Many of the non-US
files carry hand-written, live-verified fixes (nested iframes, cookie
gates, pagination quirks); regenerating those would silently throw that
work away.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')
POSTS_DIR = os.path.join(HERE, 'school_job_posts_code')
INFO_DIR = os.path.join(HERE, 'school_job_info_code')
VERIFY_FMT = os.path.join(HERE, 'careers_link_verification_{country}.csv')


def _q(text):
    """Safe single-quoted Python literal for generated source."""
    return "'" + str(text).replace('\\', '\\\\').replace("'", "\\'") + "'"


PLATFORM_POSTINGS = '''"""
Job postings scraper for school_id {sid} - {name} ({country})
ATS platform: {ats} (detected: {platform})
Careers link: {url}

{name} runs on a shared ATS platform -- every school on {platform} uses the
same underlying site software, so this calls the shared
job_postings_lib.scrape_{platform} adapter rather than duplicating
platform-specific logic here. If results for THIS ONE school need a tweak
that shouldn't apply to every {platform} school, define find_links() below
and pass it to run_checkpointed instead of editing the shared adapter.
{shared_note}
Writes school_job_posts/school_id_{sid}_job_posts.csv (school_id, post_link).
Checkpointed to school_id_{sid}_job_postings.checkpoint next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = {sid}
SCHOOL_NAME = {name_q}
CAREERS_LINK = {url_q}
ATS_PLATFORM = {ats_q}
PLATFORM = {platform_q}

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{{SCHOOL_ID}}_job_postings.checkpoint')


def main():
    result = lib.run_platform_school(SCHOOL_ID, SCHOOL_NAME, CAREERS_LINK,
                                     CHECKPOINT_PATH, platform=PLATFORM)
    err = result.get('last_error', '')
    print(f"{{SCHOOL_NAME}} (id={{SCHOOL_ID}}): status={{result['status']}} "
          f"links={{len(result['links'])}}" + (f" ERROR: {{err}}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
'''

OWN_POSTINGS = '''"""
Job postings scraper for school_id {sid} - {name} ({country})
ATS platform: own website
Careers link: {url}

No shared ATS platform adapter applies to this school -- find_links() below
is THIS SCHOOL'S OWN scraping logic, owned entirely by this file. Edit it
directly to fix or improve results for {name}; nothing here affects any
other school's script.
{verify_note}
Starting point (not a tuned answer): fetch the careers page with JS
rendered, then keep every link whose href or visible text looks
job/vacancy/posting-shaped (job_postings_lib.COMMON_JOB_URL_HINTS). If that
under- or over-collects, narrow the pattern to this site's real posting URL
shape (the single most common fix -- a generic filter also matches a site's
own navigation), add a click/scroll step via fetch_rendered's `actions`
argument, or follow pagination with a second fetch and merge the results.

Writes school_job_posts/school_id_{sid}_job_posts.csv (school_id, post_link).
Checkpointed to school_id_{sid}_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = {sid}
SCHOOL_NAME = {name_q}
CAREERS_LINK = {url_q}
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{{SCHOOL_ID}}_job_postings.checkpoint')


def find_links():
    html = lib.fetch_rendered(CAREERS_LINK)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    return lib.extract_links(html, CAREERS_LINK,
                             href_pattern=lib.COMMON_JOB_URL_HINTS,
                             text_pattern=lib.COMMON_JOB_URL_HINTS)


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{{SCHOOL_NAME}} (id={{SCHOOL_ID}}): status={{result['status']}} "
          f"links={{len(result['links'])}}" + (f" ERROR: {{err}}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
'''

INFO_TEMPLATE = '''"""
Job info scraper for school_id {sid} - {name} ({country})
ATS platform: {ats}
Careers link: {url}

Reads posting URLs from school_id_{sid}_job_postings.checkpoint (this
school's job_postings run) and classifies each one: job_title_in_post,
position_type, job_term, department_or_school, area_key_words,
deadline_of_application, position_start_date.

{info_note}
area_key_words has three parts: the subject named in the title's own rank
clause, up to 2 topics read out of the description's research sentences,
and 1 read out of its teaching sentences. Set USE_LLM = True once
ANTHROPIC_API_KEY is available for a real read of those sentences instead
of the local heuristic.

Writes school_job_info/school_id_{sid}_job_info.csv. Checkpointed to
school_id_{sid}_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = {sid}
SCHOOL_NAME = {name_q}
CAREERS_LINK = {url_q}
ATS_PLATFORM = {ats_q}
USE_LLM = False

JOB_POSTINGS_CHECKPOINT = os.path.join(
    HERE, '..', 'school_job_posts_code', f'school_id_{{SCHOOL_ID}}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{{SCHOOL_ID}}_job_info.checkpoint')

{info_body}

def main():
    result = {info_call}
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{{SCHOOL_NAME}} (id={{SCHOOL_ID}}): status={{result['status']}} "
          f"rows={{n_ok}}/{{len(result['rows'])}}" + (f" ERROR: {{err}}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
'''

BULK_BODY = ''
BULK_CALL = ("jinfo.run_school_job_info_bulk(SCHOOL_ID, CAREERS_LINK, {platform_q},\n"
             "                                            JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,\n"
             "                                            use_llm=USE_LLM)")

DETAIL_BODY = '''def fetch_detail(url):
    """This school's own detail-page logic, owned by this file. The default
    renders the page, picks the most job-title-shaped heading, and takes the
    visible text as the description. Override when a posting page needs
    something else -- a nested iframe, a cookie gate, a PDF, or a title that
    only exists in <title> (all of which came up in the non-US set)."""
    return jinfo.fetch_detail_generic(url)

'''
DETAIL_CALL = ("jinfo.run_school_job_info(SCHOOL_ID, JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,\n"
               "                                       fetch_detail_fn=fetch_detail, use_llm=USE_LLM)")


def load_verification(country):
    path = VERIFY_FMT.format(country=country)
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return {r['school_id']: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--only-verified', action='store_true',
                    help='skip schools whose careers_link verified as broken')
    ap.add_argument('--verdicts', default='',
                    help='comma-separated verdicts to generate for (e.g. "ok" or "ok,empty"); '
                         'default is every school with a careers_link')
    ap.add_argument('--force', action='store_true',
                    help='overwrite existing scripts (DISCARDS hand-written fixes)')
    args = ap.parse_args()

    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(INFO_DIR, exist_ok=True)
    verification = load_verification(args.country)
    wanted_verdicts = {v.strip() for v in args.verdicts.split(',') if v.strip()}
    if wanted_verdicts and not verification:
        sys.exit(f'--verdicts needs {VERIFY_FMT.format(country=args.country)}; run '
                 f'verify_careers_links.py {args.country} first')

    with open(MASTER, encoding='utf-8') as f:
        schools = [r for r in csv.DictReader(f)
                   if r['country'] == args.country and r['careers_link'].strip()]

    # A URL used by several schools is a shared tenant: one listing carries
    # every campus's jobs, which the note in each file calls out so nobody
    # later mistakes the duplicate counts for a bug.
    url_users = {}
    for s in schools:
        url_users.setdefault(s['careers_link'].strip(), []).append(s['name'])

    written = skipped_existing = skipped_broken = 0
    for s in schools:
        sid = s['school_id']
        url = s['careers_link'].strip()
        ver = verification.get(sid)
        if args.only_verified and ver and ver['verdict'] == 'broken':
            skipped_broken += 1
            continue
        if wanted_verdicts:
            if not ver or ver['verdict'] not in wanted_verdicts:
                skipped_broken += 1
                continue

        platform = lib.detect_platform(url)
        posts_path = os.path.join(POSTS_DIR, f'school_id_{sid}_job_postings.py')
        info_path = os.path.join(INFO_DIR, f'school_id_{sid}_job_info.py')
        if not args.force and (os.path.exists(posts_path) or os.path.exists(info_path)):
            skipped_existing += 1
            continue

        peers = url_users.get(url, [])
        shared_note = ''
        if len(peers) > 1:
            others = ', '.join(n for n in peers if n != s['name'])[:300]
            shared_note = (f"\nNOTE: {len(peers)} schools list against this same URL, so this "
                           f"listing carries every one of their postings, not just this "
                           f"school's: {others}.\n")
        verify_note = ''
        if ver:
            verify_note = (f"\nLink check ({ver['verdict']}): {ver['n_links']} posting-shaped "
                           f"links found{(' -- ' + ver['note']) if ver['note'] else ''}.\n")

        common = dict(sid=sid, name=s['name'], country=s['country'], url=url,
                      ats=s.get('ats_platform') or 'own website',
                      name_q=_q(s['name']), url_q=_q(url),
                      ats_q=_q(s.get('ats_platform') or 'own website'))

        if platform and platform in lib.PLATFORM_ADAPTERS:
            posts_src = PLATFORM_POSTINGS.format(platform=platform, platform_q=_q(platform),
                                                 shared_note=shared_note, **common)
        else:
            posts_src = OWN_POSTINGS.format(verify_note=verify_note + shared_note, **common)

        import job_info_lib as jinfo_mod
        if platform in jinfo_mod.BULK_ADAPTERS:
            info_body, info_call = BULK_BODY, BULK_CALL.format(platform_q=_q(platform))
            info_note = (f'Every posting\'s title, department and description come back from '
                         f'ONE {platform} API call (BULK_ADAPTERS), not a visit per posting.\n')
        else:
            info_body, info_call = DETAIL_BODY, DETAIL_CALL
            info_note = ''

        info_src = INFO_TEMPLATE.format(info_body=info_body, info_call=info_call,
                                        info_note=info_note, **common)

        with open(posts_path, 'w', encoding='utf-8') as f:
            f.write(posts_src)
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(info_src)
        written += 1

    print(f'{args.country}: wrote {written} school script pairs')
    if skipped_existing:
        print(f'  skipped {skipped_existing} that already exist (use --force to overwrite)')
    if skipped_broken:
        label = ('outside verdicts ' + ','.join(sorted(wanted_verdicts))) if wanted_verdicts \
            else 'whose careers_link verified as broken'
        print(f'  skipped {skipped_broken} {label}')


if __name__ == '__main__':
    main()
