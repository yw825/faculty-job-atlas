"""
MathJobs (mathjobs.org) as a posting source for schools already in the map.

Why this exists: mathjobs.org is where most mathematics, statistics and OR
faculty jobs are actually advertised, and many departments post there and
NOWHERE else -- Tufts' Applied Math assistant professorship (#28879) never
appears on jobs.tufts.edu. Before this file the corpus held zero mathjobs
links, so those openings were invisible on the map.

Cost: ONE http request. The deadline-sorted listing returns every open
position (603 on 2026-09-16) with its institution, title and deadline
inline, so no per-position page is fetched -- which matters, because
mathjobs' robots.txt sets Crawl-delay: 5 and 603 detail pages would be 50
minutes of crawling every night. /jobs is not disallowed there; only
/cgi-bin, /acjobs, /mpo and similar are.

IT NEVER ADDS A SCHOOL. A position whose institution is not already in
schools_master.csv is listed in refresh_logs/mathjobs_review_<date>.csv and
otherwise ignored. An earlier version registered unmatched institutions
automatically: it added duplicates of schools that were already there under
their campus names, admitted trading firms as "schools", and geocoded four
Korean universities into Moldova (mathjobs writes "Korea, The Republic of",
which a geocoder resolves to Transnistria). Adding schools is a decision
for a person, not a scraper.

What it writes, per school that has postings here:
  * job_postings checkpoint + posts CSV  -- merged, never replaced
  * job_info checkpoint raw[] + rows[] + info CSV, filled from the LISTING
    so the info stage finds nothing left to fetch (it skips URLs already in
    raw). Classification runs through job_info_lib's own classifier, so
    these rows are built exactly like every other school's.

MATCHING is exact, and deliberately so. schools_master.csv uses IPEDS-style
campus names ("Purdue University-Main Campus") while mathjobs writes
"Purdue University, Mathematics", so two looser rules were tried and both
produced wrong data: keying on the text before the first comma mapped every
Cal State campus onto Bakersfield, and accepting any school whose words
were a subset of the employer's filed 23 positions under the wrong
university (Central China Normal University -> Central College in Iowa,
Virginia Tech -> University of Virginia, Duke Kunshan -> Duke, Jane Street
Capital -> Capital University).

Now an institution's distinguishing words must EQUAL a school's, tried on
the institution alone and then institution + campus, with a guard so a
differing institution KIND cannot match (Cornell University is not Cornell
College; the University of Chinese Academy of Sciences is not the Chinese
Academy of Sciences). That places 516 of 603 positions; the rest go to the
review file.

Run from job-data/:
    python3 mathjobs_source.py            # nightly: match, merge, write review
    python3 mathjobs_source.py --dry-run  # report only, write nothing
"""
import argparse
import csv
import os
import re
import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib
import job_info_lib as jinfo

MASTER = os.path.join(HERE, 'schools_master.csv')
POSTS_CODE = os.path.join(HERE, 'school_job_posts_code')
INFO_CODE = os.path.join(HERE, 'school_job_info_code')

# The deadline sort is the one view that prints "(deadline YYYY/MM/DD)" on
# every row; the default sort omits it and would cost a fetch per position.
LISTING_URL = 'https://www.mathjobs.org/jobs?joblst-0-0---0-d--'
POSITION_URL = 'https://www.mathjobs.org/jobs/list/{pid}'
UA = ('faculty-job-atlas/1.0 (personal academic job map; +https://github.com/'
      'yw825/faculty-job-atlas)')

# Words that appear in hundreds of institution names and so distinguish
# nothing. Everything else in a master row's name must be matched.
STOPWORDS = {
    'the', 'of', 'at', 'and', 'for', 'in', 'university', 'universite',
    'universitat', 'college', 'institute', 'institut', 'school', 'schools',
    'department', 'dept', 'faculty', 'sciences', 'science', 'mathematics',
    'mathematical', 'statistics', 'campus', 'main', 'center', 'centre',
    'research', 'graduate', 'studies', 'program', 'programs',
}

# Those same words are exactly what separates some institutions, so a match
# whose KIND disagrees is refused: ignoring them conflated Cornell
# University with Cornell College in Iowa, and the University of Washington
# with Washington College in Maryland.
TYPE_WORDS = {'university', 'universite', 'universiteit', 'universitat',
              'college', 'institute', 'institut', 'academy', 'school',
              'polytechnic', 'conservatory', 'seminary'}
CONNECTIVES = {'the', 'of', 'at', 'and', 'in', 'for', 'a'}


def tokens(name):
    """Distinguishing words of an institution name, lowercased."""
    plain = re.sub(r'[^A-Za-z0-9 ]', ' ', name.lower())
    return [w for w in plain.split() if w not in STOPWORDS]


def _raw_words(name):
    return set(re.sub(r'[^A-Za-z0-9 ]', ' ', name.lower()).split())


def plausible_pair(employer_text, school_name):
    """Reject a word-equal match whose institution KIND disagrees.

    1. Both names state a kind and share none -- Cornell University vs
       Cornell College, University of Washington vs Washington College.
    2. One name is the other plus exactly one kind word, and the shorter
       already states a DIFFERENT kind -- University of Chinese Academy of
       Sciences vs Chinese Academy of Sciences.

    Rule 2 is deliberately not "plus any kind word": "SUNY at Geneseo" ->
    "SUNY College at Geneseo" is one school under its formal name."""
    a = _raw_words(employer_text) - CONNECTIVES
    b = _raw_words(school_name) - CONNECTIVES
    ta, tb = a & TYPE_WORDS, b & TYPE_WORDS
    if ta and tb and not (ta & tb):
        return False
    if a < b or b < a:
        shorter, longer = (a, b) if a < b else (b, a)
        extra = longer - shorter
        if len(extra) == 1 and (extra & TYPE_WORDS):
            kinds = shorter & TYPE_WORDS
            if kinds and not (extra & kinds):
                return False
    return True


def build_strict_index(rows):
    """{frozenset of distinguishing words: (school_id, name)}."""
    idx = {}
    for r in rows:
        key = frozenset(tokens(r['name']))
        if key:
            idx.setdefault(key, (r['school_id'], r['name']))
    return idx


def build_loose_index(rows):
    """Subset matching -- only ever used as a HINT in the review file."""
    idx = [(r['school_id'], r['name'], set(tokens(r['name']))) for r in rows]
    return sorted((e for e in idx if e[2]), key=lambda e: -len(e[2]))


def match_school(employer, strict_idx):
    """Exact match on distinguishing words: the institution alone, then
    institution + campus, since mathjobs writes "University of California,
    Berkeley, Mathematics" while schools_master writes "University of
    California-Berkeley" (both reduce to {california, berkeley})."""
    parts = [p.strip() for p in employer.split(',') if p.strip()]
    for n in range(1, min(3, len(parts)) + 1):
        text = ', '.join(parts[:n])
        hit = strict_idx.get(frozenset(tokens(text)))
        if not hit:
            continue
        # Check the kind guard against the comma part that actually carries
        # the institution's name; a department part would otherwise pad the
        # word difference past the guard.
        want = set(tokens(hit[1]))
        inst_part = max(parts[:n], key=lambda p: (len(set(tokens(p)) & want), -parts.index(p)))
        if plausible_pair(inst_part, hit[1]) and plausible_pair(text, hit[1]):
            return hit
    return None


def fetch_listing(session):
    r = session.get(LISTING_URL, headers={'User-Agent': UA}, timeout=60)
    r.raise_for_status()
    return r.text


def parse_listing(html):
    """-> [{employer, code, pid, title, deadline}], one per open position."""
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for ol in soup.find_all('ol', class_=lambda c: c and 'ldt' in c):
        head = ol.find_previous('h3')
        anchor = head.find('a', href=re.compile(r'^/jobs/')) if head else None
        if not anchor:
            continue
        employer = ' '.join(anchor.get_text().split())
        code = anchor['href'].rsplit('/', 1)[-1]
        for li in ol.find_all('li'):
            link = li.find('a', href=re.compile(r'/jobs/list/\d+'))
            if not link:
                continue
            pid = link['href'].rsplit('/', 1)[-1]
            title_span = li.find('span', id='j' + pid)
            text = ' '.join(li.get_text(' ').split())
            title = (' '.join(title_span.get_text().split())
                     if title_span else re.sub(r'^\[[^\]]*\]\s*', '', text))
            m = re.search(r'deadline (\d{4})/(\d{2})/(\d{2})', text)
            out.append({
                'employer': employer,
                'code': code,
                'pid': pid,
                'title': title.replace(' Apply', '').strip(),
                'deadline': '-'.join(m.groups()) if m else '',
            })
    return out


def write_review(unknown, rows):
    """Institutions this run could not place. They are NOT added as schools:
    an unmatched employer is as often an alias of a school already in the
    list (Virginia Tech, Humboldt-Universitaet zu Berlin) as a genuinely new
    institution, and that judgement is a person's to make."""
    if not unknown:
        return
    os.makedirs(os.path.join(HERE, 'refresh_logs'), exist_ok=True)
    path = os.path.join(HERE, 'refresh_logs',
                        f'mathjobs_review_{date.today().isoformat()}.csv')
    loose = build_loose_index(rows)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['institution', 'positions',
                                          'closest_existing_school', 'closest_school_id'])
        w.writeheader()
        for name, plist in sorted(unknown.items(), key=lambda kv: -len(kv[1])):
            have = set(tokens(name))
            guess = next(((sid, nm) for sid, nm, want in loose if want and want <= have),
                         ('', ''))
            w.writerow({'institution': name, 'positions': len(plist),
                        'closest_existing_school': guess[1],
                        'closest_school_id': guess[0]})
    print(f'  {len(unknown)} institutions are not in schools_master -> '
          f'{os.path.relpath(path, HERE)} (no schools added)', flush=True)


def merge_school(sid, positions, dry_run=False):
    """Merge this school's mathjobs positions into its postings checkpoint and
    pre-fill its info checkpoint, so the info stage fetches nothing here."""
    posts_ck = os.path.join(POSTS_CODE, f'school_id_{sid}_job_postings.checkpoint')
    info_ck = os.path.join(INFO_CODE, f'school_id_{sid}_job_info.checkpoint')
    urls = [POSITION_URL.format(pid=p['pid']) for p in positions]

    ckpt = lib.load_checkpoint(posts_ck)
    ckpt.setdefault('links', [])
    ckpt['school_id'] = int(sid)
    added = [u for u in urls if u not in ckpt['links']]
    ckpt['links'].extend(added)
    ckpt.setdefault('status', 'complete')
    ckpt['updated_at'] = lib.now_iso()

    info = jinfo.load_checkpoint(info_ck)
    info.setdefault('raw', {})
    info.setdefault('rows', {})
    info['school_id'] = int(sid)
    for p, url in zip(positions, urls):
        info['raw'][url] = {
            'title': p['title'],
            'description': (f"{p['title']}\n{p['employer']}\n"
                            + (f"Application deadline: {p['deadline']}\n" if p['deadline'] else '')
                            + 'Posted via MathJobs (mathjobs.org).'),
        }
    if dry_run:
        return len(added)

    lib.save_checkpoint(posts_ck, ckpt)
    lib.write_posts_csv(sid, ckpt['links'])

    links = ckpt['links']
    jinfo._classify_from_raw(int(sid), links, info, use_llm=False, llm_client=None)
    for p, url in zip(positions, urls):
        row = info['rows'].get(url)
        if row is not None and p['deadline'] and not row.get('deadline_of_application'):
            row['deadline_of_application'] = p['deadline']
    info['status'] = 'complete'
    info['updated_at'] = lib.now_iso()
    jinfo.save_checkpoint(info_ck, info)
    jinfo.write_info_csv(int(sid), info['rows'], links)
    return len(added)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    session = requests.Session()
    print('fetching the mathjobs listing (1 request)', flush=True)
    positions = parse_listing(fetch_listing(session))
    print(f'  {len(positions)} open positions across '
          f'{len({p["employer"] for p in positions})} institutions', flush=True)
    if not positions:
        sys.exit('mathjobs returned no positions -- listing shape may have changed')

    with open(MASTER, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    strict_idx = build_strict_index(rows)

    by_school, unknown = {}, {}
    for p in positions:
        hit = match_school(p['employer'], strict_idx)
        if hit:
            by_school.setdefault(hit[0], []).append(p)
        else:
            unknown.setdefault(p['employer'].split(',')[0].strip(), []).append(p)
    print(f'  {sum(len(v) for v in by_school.values())} positions at '
          f'{len(by_school)} schools already in the map', flush=True)
    write_review(unknown, rows)

    total_new = 0
    for sid, plist in sorted(by_school.items(), key=lambda kv: int(kv[0])):
        total_new += merge_school(sid, plist, dry_run=args.dry_run)
    print(f'{"would merge" if args.dry_run else "merged"} {total_new} new posting links '
          f'into {len(by_school)} schools', flush=True)


if __name__ == '__main__':
    main()
