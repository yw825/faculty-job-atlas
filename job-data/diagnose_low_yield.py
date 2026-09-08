"""
Classifies schools that returned suspiciously few postings by WHY, so the
fixes can be batched by site shape instead of written one school at a time.

Run from job-data/:
    python3 diagnose_low_yield.py US
    python3 diagnose_low_yield.py US --max-rows 3 --limit 40

Writes low_yield_diagnosis_<country>.csv:
    school_id, name, careers_link, rows_now, verdict, evidence

WHY THIS EXISTS
566 of 1,231 US schools came back with 0-3 postings, and spot checks showed
those failures are NOT one problem. St Thomas Aquinas lists its openings as
sections of prose with no per-job link at all; Northern Arizona has real
per-job links but only page 1 of them; Cal Poly Humboldt returned nothing
but its own site root. Each needs a different fix, and which fix applies is
a property of the SITE SHAPE, not of the school -- so the shapes are worth
counting before any of them are written.

VERDICTS
    inline-listing   postings are page sections, not links (no per-job href
                     exists to record; the page text IS the listing)
    paginated        real per-job links, but the page is one of several
    js-listing       page renders but the listing needs JS/interaction that
                     a plain fetch doesn't trigger
    iframe-listing   the listing lives in a nested frame
    wrong-url        the link reaches a page that isn't a job listing at all
    blocked          403/challenge/unreachable
    looks-ok-now     job links present now -- earlier run was transient
    unclear          none of the above fired
"""
import argparse
import concurrent.futures as futures
import csv
import os
import re
import sys
import threading
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')
POSTS_DIR = os.path.join(HERE, 'school_job_posts')

# Text that names a role -- used to spot postings written as prose sections.
_ROLE_TEXT_RE = re.compile(
    r'\b(professor|lecturer|instructor|faculty position|adjunct|postdoc|'
    r'post-doctoral|fellow|dean|chair|department of|visiting)\b', re.I)

_PAGING_RE = re.compile(r'[?&](?:page|pg|offset|start|skip)=\d+|rel=["\']?next', re.I)

# Matching a bare capitalised heading ("Mathematics") was tried as a way to
# catch inline postings whose heading names only the discipline, and had to
# be dropped: it matches every navigation item on the page too, which put
# St Thomas Aquinas at 120 "inline" hits and made every school look like an
# inline listing. How often the page says "professor"/"faculty position" at
# all turns out to separate them cleanly on its own -- St Thomas Aquinas
# scores 29 against Northern Arizona's 4.
_PAGING_TEXT_RE = re.compile(r'^\s*(?:next|more|load more|show more|older|»|>>|\d+)\s*$', re.I)

# An iframe worth caring about points at something recruitment-shaped.
_JOB_FRAME_SRC_RE = re.compile(
    r'job|career|recruit|vacanc|position|hiring|talent|workday|taleo|icims|'
    r'peopleadmin|greenhouse|lever|smartrecruiters|paycom|adp', re.I)

_WALL_RE = re.compile(
    r'\b(?:just a moment|checking your browser|verify you are human|'
    r'access denied|forbidden|enable javascript|enable cookies)\b', re.I)

# A careers link that actually lands on something else entirely.
_WRONG_PAGE_RE = re.compile(
    r'\b(?:student employment|career services|career center|internship|'
    r'alumni career|advising|resume|cover letter workshop)\b', re.I)

_lock = threading.Lock()


def rows_for(school_id):
    path = os.path.join(POSTS_DIR, f'school_id_{school_id}_job_posts.csv')
    if not os.path.exists(path):
        return -1
    with open(path, encoding='utf-8') as f:
        return sum(1 for _ in csv.DictReader(f))


def signals(html, url):
    """Everything the classifier looks at, gathered in one pass."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    job_links = set(lib.extract_links(html, url, href_pattern=lib.COMMON_JOB_URL_HINTS,
                                      text_pattern=lib.COMMON_JOB_URL_HINTS))

    # Role-naming text that is NOT inside a link: the signature of a posting
    # written as a section of the page rather than linked to. Counted two
    # ways because a heading often names only the DISCIPLINE ("EXERCISE
    # SCIENCE", "COMPUTER SCIENCE") while the rank word sits in the prose
    # underneath -- requiring the rank word in the heading itself found
    # only 2 of St Thomas Aquinas's 4 postings.
    inline = 0
    for el in soup.find_all(['h2', 'h3', 'h4', 'h5', 'strong', 'b', 'li', 'summary']):
        if el.find_parent('a'):
            continue
        text = el.get_text(' ', strip=True)
        if 3 < len(text) < 120 and _ROLE_TEXT_RE.search(text):
            inline += 1
    body_text = soup.get_text(' ', strip=True)
    role_mentions = len(_ROLE_TEXT_RE.findall(body_text))

    paging = bool(_PAGING_RE.search(html))
    if not paging:
        for a in soup.find_all('a', href=True):
            if _PAGING_TEXT_RE.match(a.get_text(' ', strip=True) or ''):
                paging = True
                break

    body = body_text
    return {
        'job_links': len(job_links),
        'inline': inline,
        'role_mentions': role_mentions,
        'paging': paging,
        # Only frames that could plausibly HOST a listing. Counting every
        # iframe made chat and analytics widgets look like embedded job
        # boards -- St Thomas Aquinas carries 4 such frames and was
        # misfiled as an iframe listing because of them.
        'iframes': sum(1 for f in soup.find_all('iframe')
                       if _JOB_FRAME_SRC_RE.search(f.get('src') or '')),
        'text_len': len(body),
        'wall': bool(_WALL_RE.search(body[:4000])),
        'wrong_page': bool(_WRONG_PAGE_RE.search(body[:3000])) and not job_links,
    }


def classify(sig, static_only):
    """Verdict plus the evidence that produced it."""
    if sig is None:
        return 'blocked', 'page could not be fetched'
    ev = (f"links={sig['job_links']} inline={sig['inline']} "
          f"roles={sig['role_mentions']} paging={'y' if sig['paging'] else 'n'} "
          f"iframes={sig['iframes']} text={sig['text_len']}")

    if sig['wall']:
        return 'blocked', ev + ' wall/challenge'
    if sig['job_links'] >= 8:
        return 'looks-ok-now', ev

    # Ordered by how much the signal actually tells us. A page that says
    # "professor"/"faculty position" many times over while offering nothing
    # to click is prose, and says so more loudly than an ambiguous frame
    # does -- St Thomas Aquinas scores 29 role mentions AND carries frames
    # whose src mentions careers, and it is unambiguously a prose listing.
    if sig['job_links'] <= 3 and sig['role_mentions'] >= 10:
        return 'inline-listing', ev
    if sig['iframes'] >= 1 and sig['job_links'] <= 3:
        return 'iframe-listing', ev
    if sig['job_links'] <= 3 and (sig['inline'] >= 3 or sig['role_mentions'] >= 6):
        return 'inline-listing', ev

    # Pagination only counts when there is a real set of per-job links to
    # be a page OF -- a stray ?page= in site navigation is not evidence.
    if sig['job_links'] >= 3 and sig['paging']:
        return 'paginated', ev
    if sig['iframes'] >= 1 and sig['job_links'] <= 3:
        return 'iframe-listing', ev
    if sig['wrong_page']:
        return 'wrong-url', ev
    if sig['job_links'] == 0:
        return 'js-listing' if static_only else 'no-listing-found', ev
    # 1-7 links with nothing else to explain it: too few to trust, but no
    # single shape identified. Deliberately NOT called ok.
    return 'unclear', ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--max-rows', type=int, default=3,
                    help='diagnose schools at or below this many posting rows')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8)
    args = ap.parse_args()

    with open(MASTER, encoding='utf-8') as f:
        schools = [r for r in csv.DictReader(f)
                   if r['country'] == args.country and r['careers_link'].strip()]
    targets = []
    for s in schools:
        n = rows_for(s['school_id'])
        if 0 <= n <= args.max_rows:
            targets.append((s, n))
    if args.limit:
        targets = targets[:args.limit]
    print(f'{args.country}: diagnosing {len(targets)} schools with <= {args.max_rows} rows',
          flush=True)

    results = {}
    needs_browser = []

    def static_pass(item):
        s, _n = item
        try:
            status, html = lib.fetch_static(s['careers_link'])
        except Exception:
            return None
        if not status or status >= 400 or not html or len(html) < 1500:
            return None
        return signals(html, s['careers_link'])

    done = 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fut = {pool.submit(static_pass, t): t for t in targets}
        for f in futures.as_completed(fut):
            s, n = fut[f]
            try:
                sig = f.result()
            except Exception:
                sig = None
            # A page that yields nothing over plain HTTP has to be seen with
            # JS before "no listing here" can be believed.
            if sig is None or sig['job_links'] == 0:
                needs_browser.append((s, n, sig))
            else:
                results[s['school_id']] = classify(sig, static_only=True)
            done += 1
            if done % 50 == 0:
                print(f'  static {done}/{len(targets)}', flush=True)

    print(f'  rendering {len(needs_browser)} that showed no listing over plain HTTP',
          flush=True)
    for i, (s, n, _sig) in enumerate(needs_browser, 1):
        try:
            html = lib.fetch_rendered(s['careers_link'], wait_ms=3500) or ''
            sig = None if lib.is_fetch_failure(html) or len(html) < 1500 else \
                signals(html, s['careers_link'])
        except Exception:
            sig = None
        results[s['school_id']] = classify(sig, static_only=False)
        if i % 25 == 0:
            print(f'  rendered {i}/{len(needs_browser)}', flush=True)

    out = os.path.join(HERE, f'low_yield_diagnosis_{args.country}.csv')
    rows = []
    for s, n in targets:
        verdict, ev = results.get(s['school_id'], ('unclear', 'not checked'))
        rows.append({'school_id': s['school_id'], 'name': s['name'],
                     'careers_link': s['careers_link'], 'rows_now': n,
                     'verdict': verdict, 'evidence': ev})
    rows.sort(key=lambda r: int(r['school_id']))
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['school_id', 'name', 'careers_link',
                                          'rows_now', 'verdict', 'evidence'])
        w.writeheader()
        w.writerows(rows)

    tally = {}
    for r in rows:
        tally[r['verdict']] = tally.get(r['verdict'], 0) + 1
    print(f'\nwrote {out}')
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f'  {v:5d}  {k}')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
