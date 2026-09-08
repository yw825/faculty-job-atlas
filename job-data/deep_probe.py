"""
Visits every low-yield school's careers page and works out, structurally,
which links on it are the postings -- without relying on any keyword.

Run from job-data/:
    python3 deep_probe.py US --max-rows 10
    python3 deep_probe.py US --max-rows 10 --limit 40

Writes deep_probe_<country>.csv:
    school_id, name, careers_link, rows_now, best_pattern, candidates, note

WHY STRUCTURAL AND NOT KEYWORDS
Every keyword list we have tried leaks in both directions. UCLA's postings
are /JPF11265, /JPF11233, ... -- no job word in the URL and none in the
link text either, so a keyword matcher finds zero on a page holding 215
real openings. Meanwhile "careers", "jobs" and "positions" match a site's
own navigation on nearly every school.

What a listing page actually looks like, on any platform, is a RUN OF
SIBLING LINKS SHARING ONE URL SHAPE and differing only where the id or
slug goes. So links are grouped by their template -- path with the varying
segment replaced by a placeholder, plus the set of query keys -- and the
biggest credible group is taken as the postings. Navigation fails this
test because nav links differ from each other in shape, not in one slot.

Each group is scored, not just counted, because a paginator ("?page=1..9")
is also a run of siblings. Distinct anchor text is what separates them: 20
postings have 20 different titles, while 9 pagination links read
"1","2","3". A group whose anchor texts are mostly identical or numeric is
rejected for that reason.
"""
import argparse
import concurrent.futures as futures
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urlsplit, urljoin

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')
POSTS_DIR = os.path.join(HERE, 'school_job_posts')

# Segments that vary per posting: numeric ids, hashes, uuids, and the
# mixed id-and-slug forms ATSs like ("JPF11265", "45312-assistant-prof").
_VARYING = re.compile(
    r'^(?:\d+|[0-9a-f]{8,}|[A-Z]{2,5}\d{3,}|\d+[-_].+|.+[-_]\d{3,})$', re.I)

_NAV_TEXT = re.compile(
    r'^\s*(?:\d+|next|prev|previous|more|first|last|»|«|>>|<<|home|apply|'
    r'search|view|details?|read more|learn more|back)\s*$', re.I)


def templatize(url, base):
    """A URL reduced to its shape: varying segments become <*>.

    The LAST segment is also treated as varying when it reads like a title
    slug (hyphenated or long), because blog-style careers pages name each
    posting in the URL itself -- Southern Arkansas publishes
    /human-resources/2026/06/24/instructor-of-agriculture/ and
    /human-resources/2026/05/05/assistant-professor-.../, which share no
    literal shape at all until the slug is treated as the variable."""
    parts = urlsplit(urljoin(base, url))
    segs = [s for s in parts.path.split('/') if s]
    shaped = ['<*>' if _VARYING.match(s) else s for s in segs]
    if shaped and shaped[-1] != '<*>':
        last = segs[-1]
        if last.count('-') >= 2 or len(last) > 15:
            shaped[-1] = '<*>'
    qkeys = ','.join(sorted({kv.split('=')[0] for kv in parts.query.split('&') if kv}))
    return f"{parts.netloc}/{'/'.join(shaped)}" + (f'?{qkeys}' if qkeys else '')


def find_posting_groups(html, base):
    """[(template, [(url, text)...], score)] best-scoring group first."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    groups = defaultdict(list)
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        absolute = urljoin(base, href)
        if not absolute.startswith('http'):
            continue
        groups[templatize(href, base)].append((absolute, a.get_text(' ', strip=True)))

    scored = []
    for template, members in groups.items():
        urls = {u for u, _t in members}
        if len(urls) < 2:
            continue                      # a listing has sibling links
        if '<*>' not in template:
            continue                      # nothing varies -> not a listing
        texts = [t for _u, t in members if t]
        distinct = {t.lower() for t in texts}
        # Pagination and "read more" runs: many links, near-identical text.
        meaningful = [t for t in distinct if not _NAV_TEXT.match(t) and len(t) > 3]
        if len(meaningful) < 2:
            continue
        # Prefer many siblings AND many distinct, title-like texts.
        avg_len = sum(len(t) for t in meaningful) / max(len(meaningful), 1)
        score = len(urls) * min(len(meaningful) / max(len(urls), 1), 1.0) * min(avg_len / 20, 2.0)
        scored.append((template, members, round(score, 1)))
    scored.sort(key=lambda g: -g[2])
    return scored


def probe(school_and_n):
    s, n = school_and_n
    url = s['careers_link'].strip()
    if not url:
        return (s, n, '', 0, 'no careers_link')
    try:
        html = lib.fetch_rendered(url, wait_ms=5000) or ''
    except Exception as e:
        return (s, n, '', 0, f'{type(e).__name__}')
    if lib.is_fetch_failure(html) or len(html) < 1000:
        return (s, n, '', 0, 'page did not load')
    groups = find_posting_groups(html, url)
    if not groups:
        # No sibling links at all can still mean a real listing -- some
        # schools write each opening as a section of the page with nothing
        # to click (confirmed on St Thomas Aquinas and Dubuque). Counting
        # role mentions in the body distinguishes that from a page with
        # genuinely nothing on it.
        from bs4 import BeautifulSoup
        text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
        roles = len(re.findall(
            r'\b(?:professor|lecturer|instructor|faculty position|adjunct|'
            r'postdoc|dean|chair)\b', text, re.I))
        if roles >= 6:
            return (s, n, 'INLINE-TEXT', roles, f'inline listing, {roles} role mentions')
        return (s, n, '', 0, 'no repeated link pattern found')
    template, members, score = groups[0]
    return (s, n, template, len({u for u, _ in members}), f'score={score}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--max-rows', type=int, default=10)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    with open(MASTER, encoding='utf-8') as f:
        schools = [r for r in csv.DictReader(f)
                   if r['country'] == args.country and r['careers_link'].strip()]
    targets = []
    for s in schools:
        p = os.path.join(POSTS_DIR, f"school_id_{s['school_id']}_job_posts.csv")
        n = 0
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                n = sum(1 for _ in csv.DictReader(f))
        if n <= args.max_rows:
            targets.append((s, n))
    if args.limit:
        targets = targets[:args.limit]

    print(f'{args.country}: deep-probing {len(targets)} schools with <= {args.max_rows} rows',
          flush=True)

    out = os.path.join(HERE, f'deep_probe_{args.country}.csv')
    rows = []
    # Serial: every probe is a full browser render, and Playwright's sync
    # API cannot be driven from worker threads.
    for i, t in enumerate(targets, 1):
        s, n, template, count, note = probe(t)
        rows.append({'school_id': s['school_id'], 'name': s['name'],
                     'careers_link': s['careers_link'], 'rows_now': n,
                     'best_pattern': template, 'candidates': count, 'note': note})
        if i % 20 == 0:
            found = sum(1 for r in rows if r['candidates'] > r['rows_now'])
            print(f'  {i}/{len(targets)} -- {found} so far have more postings than we hold',
                  flush=True)
            with open(out, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)

    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    gain = [r for r in rows if r['candidates'] > r['rows_now']]
    print(f'\nwrote {out}')
    print(f'  {len(gain)} schools have MORE postings on the page than we captured')
    print(f'  {sum(r["candidates"] for r in gain)} candidate postings vs '
          f'{sum(r["rows_now"] for r in gain)} currently held')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
