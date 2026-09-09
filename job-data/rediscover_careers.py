"""
Finds the REAL careers page for schools whose configured careers_link
doesn't lead to one, by starting from the school's own homepage.

Run from job-data/:
    python3 rediscover_careers.py --ids-file /tmp/zero_ids.json --dry-run
    python3 rediscover_careers.py --ids-file /tmp/zero_ids.json --apply

Writes careers_rediscovery.csv:
    school_id, name, old_url, new_url, evidence, verdict

WHY THIS IS NEEDED
Most of the schools sitting at zero postings are not scraping failures --
their careers_link points somewhere that was never a job board. All 12
"Ellucian CRM Recruit" schools point at a student ADMISSIONS form
(/Apply/Account/Create, "Application Deadlines", "Demographic
Information"); the Symplicity ones point at a student career-services
portal that now 404s. No adapter can extract faculty postings from those,
because the postings were never there.

So instead of scraping harder, this walks the school's own site: fetch the
homepage, follow the links that name employment, and keep the page that
actually carries job postings. A candidate is accepted only on POSITIVE
evidence -- repeated per-job links, or the inline posting sections used by
schools that write openings as prose -- never merely because a page says
"careers", since a university's nav says that on every page.

Deliberately NOT accepted: student job boards, career-services/advising
pages, and HR benefits pages, all of which live one click from the same
nav and mention employment constantly.
"""
import argparse
import concurrent.futures as futures
import csv
import json
import os
import re
import sys
from urllib.parse import urljoin, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_postings_lib as lib

MASTER = os.path.join(HERE, 'schools_master.csv')

# Link text/href that plausibly leads to a staff/faculty careers page.
# Spanish included: the Puerto Rico campuses publish nothing in English,
# and an English-only pattern found no careers page for any of them --
# their nav says "Recursos Humanos".
_CAREERS_HINT_RE = re.compile(
    r'employment|career|job|vacanc|work[- ]?(?:with|for|at)|hiring|'
    r'human[- ]resources|\bhr\b|join[- ](?:us|our)|opportunit|'
    r'empleo|recursos[- ]humanos|vacante|trabaj|convocatoria', re.I)

# ...but not to the STUDENT side of the same site. These are the pages that
# cost the most false accepts: they sit in the same nav, use the same
# words, and have nothing to do with faculty hiring.
_STUDENT_SIDE_RE = re.compile(
    r'student[- ]employment|student[- ]jobs?|career[- ](?:services|center|centre|'
    r'development|coaching|advising|readiness|fair)|internship|handshake|'
    r'symplicity|alumni|resume|cover[- ]letter|advising|admission|apply/account|'
    r'prospect|scholarship|financial[- ]aid|work[- ]study|'
    r'oportunidades[- ]educativas|admisiones|estudiante|beca', re.I)

# Paths worth trying when the homepage yields nothing.
_GUESS_PATHS = [
    '/careers', '/jobs', '/employment', '/hr/careers', '/hr/employment',
    '/human-resources/careers', '/human-resources/employment',
    '/about/careers', '/about/employment', '/offices/human-resources/careers',
    '/administration/human-resources/employment', '/work-here', '/hr/jobs',
]


def job_evidence(html, url):
    """(n_postings, n_sections) -- how much this page looks like a listing.

    Counts links that are STRUCTURALLY postings (a run of siblings sharing
    one URL shape, with distinct title-like anchor text -- deep_probe's
    test) rather than links carrying a job word. Word-matching accepts any
    university page, because "Careers"/"Jobs"/"Employment" sit in the nav
    of all of them: it put Georgia State's student "College to Career" page
    at 90 job links and Hendrix's "Career Success" office ahead of its
    actual HR page. A student careers page has the vocabulary but not the
    structure -- it has no run of per-posting links.
    """
    import deep_probe
    try:
        groups = deep_probe.find_posting_groups(html, url)
    except Exception:
        groups = []
    best = 0
    for _template, members, _score in groups[:3]:
        urls = {u for u, _t in members if u.rstrip('/') != url.rstrip('/')}
        best = max(best, len(urls))
    try:
        sections = lib.extract_inline_postings(html, url)
    except Exception:
        sections = []
    return best, len(sections), groups


# A homepage is not a careers page, however many job words its nav
# carries -- Marian's "/index.php" was accepted on 5 such links.
_ROOT_PATH_RE = re.compile(r'^/?(?:index\.(?:php|html?|aspx)|home|default\.aspx)?/?$', re.I)


def plausible_candidate(url, base):
    """Reject a candidate before it is ever fetched.

    Off-site links are allowed ONLY when they point at a recognised ATS
    host, because a real careers page often lives on one (jobs.lssu.edu,
    a Workday tenant). Without that restriction the hunt wanders off the
    university's site entirely -- Inter American was "found" at
    onetonline.org, a federal occupations database."""
    parts = urlsplit(url)
    if _ROOT_PATH_RE.match(parts.path or '/'):
        return False
    if parts.netloc != urlsplit(base).netloc:
        host = parts.netloc.lower()
        same_org = urlsplit(base).netloc.lower().split('.')[-2:]
        if host.split('.')[-2:] != same_org:
            try:
                if not lib.detect_platform(url):
                    return False
            except Exception:
                return False
    return True


def accepted(n_links, n_sections):
    return n_links >= 5 or n_sections >= 2


def candidates_from_home(html, base):
    """Careers-ish links on the homepage, best first."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    scored = {}
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        full = urljoin(base, href)
        if not full.startswith('http'):
            continue
        text = a.get_text(' ', strip=True)
        blob = f'{text} {full}'
        if not _CAREERS_HINT_RE.search(blob) or _STUDENT_SIDE_RE.search(blob):
            continue
        # Prefer same-host pages and ones whose LINK TEXT (not just the
        # URL) names employment -- a footer "Careers" beats a stray /jobs
        # buried in a query string.
        score = 0
        if _CAREERS_HINT_RE.search(text):
            score += 2
        if urlsplit(full).netloc == urlsplit(base).netloc:
            score += 1
        if re.search(r'employment|career', full, re.I):
            score += 1
        scored[full] = max(scored.get(full, 0), score)
    return [u for u, _s in sorted(scored.items(), key=lambda kv: -kv[1])][:6]


def links_look_like_postings(groups, page_url):
    """Open up to two of the candidate's own links and check they read as
    job postings.

    Structure alone is not enough: a university's student pages are also a
    run of same-shaped sibling links, so Georgia State's "College to
    Career" scored 38 and UC Denver's "student-finances" 11. Only the
    linked PAGES separate a job board from a well-organised brochure."""
    import validate_and_apply as val
    for _template, members, _score in groups[:2]:
        urls = [u for u, _t in members if u.rstrip('/') != page_url.rstrip('/')]
        for candidate in urls[:2]:
            try:
                # A link into a known ATS is a posting by construction --
                # no need to read it, and often impossible to.
                if lib.detect_platform(candidate):
                    return True
                status, html = lib.fetch_static(candidate)
                # A block is evidence of a real job board, not of a
                # brochure page: WKU's postings live on interviewexchange
                # and every one of them answers 403 to a plain fetch.
                # Condemning those was exactly the error that wrongly
                # wrote off 81 schools during link verification.
                if status in (401, 403, 429):
                    return True
                if not html or status != 200 or len(html) < 800:
                    continue
                ok, _ev = val.looks_like_posting(html)
                if ok:
                    return True
            except Exception:
                continue
    return False


def try_page(url):
    """(n_links, n_sections, note) for one candidate, cheapest route first."""
    html = ''
    try:
        status, static_html = lib.fetch_static(url)
        if status == 200 and static_html and len(static_html) > 1500:
            html = static_html
    except Exception:
        pass
    if html:
        n_links, n_sections, groups = job_evidence(html, url)
        if accepted(n_links, n_sections):
            # Sections are their own evidence -- the postings are the page.
            if n_sections >= 2 or links_look_like_postings(groups, url):
                return n_links, n_sections, 'static'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids-file', required=True)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--out', default='careers_rediscovery.csv')
    args = ap.parse_args()

    ids = [str(i) for i in json.load(open(args.ids_file))]
    master = {r['school_id']: r for r in csv.DictReader(open(MASTER))}
    targets = [master[i] for i in ids if i in master]
    if args.limit:
        targets = targets[:args.limit]
    print(f'rediscovering careers pages for {len(targets)} schools', flush=True)

    results = {}
    needs_browser = []

    def static_hunt(s):
        base = (s.get('base_url') or '').strip()
        if not base:
            return None
        try:
            status, home = lib.fetch_static(base)
        except Exception:
            return None
        if not home or (status or 0) >= 400:
            return None
        for url in candidates_from_home(home, base):
            if not plausible_candidate(url, base):
                continue
            got = try_page(url)
            if got:
                return (url, got)
        for path in _GUESS_PATHS:
            url = urljoin(base, path)
            got = try_page(url)
            if got:
                return (url, got)
        return None

    done = 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fut = {pool.submit(static_hunt, s): s for s in targets}
        for f in futures.as_completed(fut):
            s = fut[f]
            try:
                got = f.result()
            except Exception:
                got = None
            if got:
                url, (nl, ns, how) = got
                results[s['school_id']] = (url, f'links={nl} sections={ns} via {how}', 'found')
            else:
                needs_browser.append(s)
            done += 1
            if done % 25 == 0:
                print(f'  static {done}/{len(targets)} -- {len(results)} found', flush=True)

    print(f'  {len(needs_browser)} need a browser', flush=True)
    for i, s in enumerate(needs_browser, 1):
        base = (s.get('base_url') or '').strip()
        found = None
        if base:
            try:
                home = lib.fetch_rendered(base, wait_ms=3500) or ''
                if not lib.is_fetch_failure(home):
                    for url in candidates_from_home(home, base):
                        if not plausible_candidate(url, base):
                            continue
                        html = lib.fetch_rendered(url, wait_ms=4000) or ''
                        if lib.is_fetch_failure(html):
                            continue
                        nl, ns, groups = job_evidence(html, url)
                        if accepted(nl, ns) and (ns >= 2 or
                                                 links_look_like_postings(groups, url)):
                            found = (url, f'links={nl} sections={ns} via browser')
                            break
            except Exception:
                pass
        results[s['school_id']] = found + ('found',) if found else ('', '', 'not-found')
        if i % 10 == 0:
            n = sum(1 for v in results.values() if v[2] == 'found')
            print(f'  browser {i}/{len(needs_browser)} -- {n} found total', flush=True)

    rows = []
    for s in targets:
        url, ev, verdict = results.get(s['school_id'], ('', '', 'not-found'))
        rows.append({'school_id': s['school_id'], 'name': s['name'],
                     'old_url': s['careers_link'], 'new_url': url,
                     'evidence': ev, 'verdict': verdict})
    out = os.path.join(HERE, args.out)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    found = [r for r in rows if r['verdict'] == 'found']
    print(f'\nwrote {out}\n  found a real careers page for {len(found)}/{len(rows)}')

    if args.apply and found:
        all_rows = list(csv.DictReader(open(MASTER)))
        fields = all_rows[0].keys()
        new = {r['school_id']: r['new_url'] for r in found}
        for r in all_rows:
            if r['school_id'] in new:
                r['careers_link'] = new[r['school_id']]
                r['notes'] = (r.get('notes') or '') + ' | careers_link rediscovered from homepage'
        with open(MASTER, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(all_rows)
        print(f'  updated schools_master.csv for {len(new)} schools')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
