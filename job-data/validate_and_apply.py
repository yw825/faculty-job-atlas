"""
Takes the link pattern deep_probe.py found for a school, OPENS a couple of
the links it points at, and only writes that pattern into the school's
scraper if those pages actually read like job postings.

Run from job-data/:
    python3 validate_and_apply.py US --dry-run
    python3 validate_and_apply.py US

Writes pattern_validation_<country>.csv:
    school_id, name, pattern, sampled_url, verdict, evidence

WHY VALIDATE RATHER THAN JUST APPLY
deep_probe picks the biggest run of same-shaped sibling links on the page,
which is the postings on a real listing -- but on a school whose careers
page has no postings at all, the biggest such run is whatever else the
page repeats. Franklin's best pattern is /blog/<*>, Excelsior's is
/program/<*>, Walsh's is the top-level site nav. Applying those blindly
would fill the dataset with blog posts and degree programmes and call it
faculty hiring, which is worse than the empty file it replaced.

So each candidate pattern is checked by fetching two of its own links and
asking whether the page looks like ONE job posting: does it name a role,
and does it carry the furniture a posting has (apply / qualifications /
responsibilities / salary / deadline)? A programme page mentions none of
that, a blog post almost never does.
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
POSTS_CODE = os.path.join(HERE, 'school_job_posts_code')

_ROLE_RE = re.compile(
    r'\b(professor|lecturer|instructor|faculty|adjunct|postdoc|post-doctoral|'
    r'dean|provost|chair|coordinator|director|technician|scientist|'
    r'researcher|specialist|counselor|librarian|nurse)\b', re.I)

# The paperwork a real posting carries and a programme/blog page does not.
# Deliberately excludes "full-time", "part-time" and "equal opportunity
# employer": those sit in the nav or footer of entire university sites, so
# they fire on any page at all. William Woods' degree page for "Associate
# of Arts in Liberal Arts" was accepted on exactly that kind of evidence.
_POSTING_FURNITURE_RE = re.compile(
    r'\b(minimum qualifications|preferred qualifications|required qualifications|'
    r'how to apply|to apply, |application deadline|responsibilities include|'
    r'essential duties|position summary|job summary|salary range|'
    r'review of applications|application materials|letters of recommendation|'
    r'curriculum vitae|cover letter)\b', re.I)

# A posting's own title names the job. A degree page's title names a degree.
_DEGREE_TITLE_RE = re.compile(
    r'\b(associate|bachelor|master|doctor|b\.?[as]\.?|m\.?[as]\.?|ph\.?d|'
    r'degree|programme?|major|minor|certificate|curriculum|course)\b', re.I)


def looks_like_posting(html):
    """(bool, evidence) for a single fetched page.

    The page's own <title>/<h1> has to name a role and must not read as a
    degree, because body text alone can't tell a job posting from any other
    page on a university site -- nav and footer supply role words and
    boilerplate everywhere."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)
    heading = ' '.join(filter(None, [
        soup.title.get_text(' ', strip=True) if soup.title else '',
        soup.h1.get_text(' ', strip=True) if soup.h1 else '']))

    title_role = bool(_ROLE_RE.search(heading))
    title_degree = bool(_DEGREE_TITLE_RE.search(heading))
    furniture = len(set(m.group(0).lower() for m in _POSTING_FURNITURE_RE.finditer(text)))

    # Two or more of the tightened posting phrases is the reliable signal on
    # its own: across a checked set, real postings scored 3-6 while a degree
    # page scored 1 and a blog post 0. Requiring a role word in the TITLE as
    # well was tried and rejected -- it threw out real UC postings whose
    # heading is a position number, and "PhD" in a title made a genuine
    # professorship read as a degree page. A single phrase still passes when
    # the heading names a role and doesn't read as a degree.
    ok = furniture >= 2 or (furniture >= 1 and title_role and not title_degree)
    return ok, (f'title_role={int(title_role)} degree={int(title_degree)} '
                f'furniture={furniture} len={len(text)}')


def sample_links(url, pattern):
    """Re-render the listing and pull the links matching `pattern`."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    sys.path.insert(0, HERE)
    import deep_probe

    html = lib.fetch_rendered(url, wait_ms=5000) or ''
    if lib.is_fetch_failure(html) or len(html) < 1000:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        if deep_probe.templatize(href, url) == pattern:
            full = urljoin(url, href)
            if full not in out:
                out.append(full)
    return out


FIND_LINKS_TEMPLATE = '''def find_links():
    """CUSTOMIZED: postings on this site are the links matching one repeated
    URL shape, found structurally rather than by keyword and then confirmed
    by opening two of them and checking they read like job postings
    ({evidence}).

        {pattern}

    The generic job-word filter returned {had} link(s) here against {found}
    actually on the page -- this site's posting URLs carry no job word at
    all, which is why matching on words missed them."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import deep_probe

    html = lib.fetch_rendered(CAREERS_LINK, wait_ms=5000)
    if lib.is_fetch_failure(html):
        raise RuntimeError(html)
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        if deep_probe.templatize(href, CAREERS_LINK) == POSTING_PATTERN:
            full = urljoin(CAREERS_LINK, href)
            if full not in out:
                out.append(full)
    return out
'''


def rewrite_script(school_id, pattern, evidence, had, found):
    path = os.path.join(POSTS_CODE, f'school_id_{school_id}_job_postings.py')
    if not os.path.exists(path):
        return False
    with open(path, encoding='utf-8') as f:
        src = f.read()
    start = src.find('def find_links():')
    end = src.find('def main():')
    if start == -1 or end == -1:
        return False
    new_fn = FIND_LINKS_TEMPLATE.format(pattern=pattern, evidence=evidence,
                                        had=had, found=found)
    src = (src[:start] + f'POSTING_PATTERN = {pattern!r}\n\n\n' + new_fn + '\n\n' + src[end:])
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    probe_path = os.path.join(HERE, f'deep_probe_{args.country}.csv')
    with open(probe_path, encoding='utf-8') as f:
        probe = [r for r in csv.DictReader(f)
                 if r['best_pattern'] and r['best_pattern'] != 'INLINE-TEXT'
                 and int(r['candidates']) > int(r['rows_now'])]
    probe.sort(key=lambda r: -(int(r['candidates']) - int(r['rows_now'])))
    if args.limit:
        probe = probe[:args.limit]

    print(f'{args.country}: validating {len(probe)} candidate patterns', flush=True)
    results = []
    applied = 0
    for i, r in enumerate(probe, 1):
        sid, pattern = r['school_id'], r['best_pattern']
        links = sample_links(r['careers_link'], pattern)
        if not links:
            results.append((sid, r['name'], pattern, '', 'no-links-now', 'pattern not found on reload'))
            continue
        verdict, evidence, sampled = 'rejected', '', links[0]
        checks = []
        for candidate in links[:2]:
            try:
                status, html = lib.fetch_static(candidate)
                if not html or status != 200 or len(html) < 800:
                    html = lib.fetch_rendered(candidate, wait_ms=3000) or ''
                ok, ev = looks_like_posting(html)
            except Exception as e:
                ok, ev = False, type(e).__name__
            checks.append((ok, ev))
        if any(ok for ok, _ in checks):
            verdict = 'accepted'
            evidence = '; '.join(ev for _ok, ev in checks)
            if not args.dry_run and rewrite_script(sid, pattern, evidence,
                                                   r['rows_now'], len(links)):
                applied += 1
        else:
            evidence = '; '.join(ev for _ok, ev in checks)
        results.append((sid, r['name'], pattern, sampled, verdict, evidence))
        if i % 20 == 0:
            acc = sum(1 for x in results if x[4] == 'accepted')
            print(f'  {i}/{len(probe)} -- {acc} accepted', flush=True)

    out = os.path.join(HERE, f'pattern_validation_{args.country}.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['school_id', 'name', 'pattern', 'sampled_url', 'verdict', 'evidence'])
        w.writerows(results)

    acc = sum(1 for r in results if r[4] == 'accepted')
    rej = sum(1 for r in results if r[4] == 'rejected')
    print(f'\nwrote {out}')
    print(f'  accepted {acc} | rejected {rej} | scripts rewritten {applied}')
    try:
        lib.close_browser()
    except Exception:
        pass


if __name__ == '__main__':
    main()
