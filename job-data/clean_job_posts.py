"""
Removes non-posting URLs from the school_job_posts/*.csv files.

Run from job-data/:
    python3 clean_job_posts.py --dry-run          # report only, change nothing
    python3 clean_job_posts.py --dry-run --school 2
    python3 clean_job_posts.py                    # rewrite the CSVs
    python3 clean_job_posts.py --report clean_report.csv

WHY
The per-school scrapers keep every link that looks job-shaped, which also
matches a careers site's own furniture: its home page, its search page, its
category pages, its campus pages. University of Alaska's file, for example,
opened with twelve of those before the first real posting -- /home-page,
/jobs/search, /jobs/search/faculty-jobs, /university-of-alaska-anchorage.

Rather than tighten 900-odd regexes by hand, this uses the one thing that
holds across sites: within a school, REAL POSTINGS ARE NUMEROUS AND SHARE A
SHAPE, while furniture is sparse and structurally different. The dominant
URL template is taken as the posting template, and rows outside it are
dropped only when they also look like furniture on their own merits.

Deliberately conservative. Every rule here can only fire with corroboration,
and a school whose rows would ALL be dropped keeps everything instead --
losing real postings is far worse than keeping a few junk rows, which the
later title-based pass can still catch.
"""
import argparse
import csv
import glob
import os
import re
from collections import Counter, defaultdict
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(HERE, 'school_job_posts')

# Path segments that name a section of a careers site, never one job.
_NAV_SEGMENT = re.compile(
    r'^(?:home|home-?page|index|default|main|search|browse|find|all|list|listing|listings|'
    r'jobs|job|careers?|vacancies|vacancy|opportunities|openings|positions|postings|'
    r'employment|recruitment|apply|application|login|log-?in|signin|sign-?in|register|'
    r'account|profile|dashboard|alerts?|subscribe|notify|rss|feed|sitemap|help|faq|'
    r'about|about-?us|contact|contact-?us|benefits|why-?work|life|culture|diversity|'
    r'students?|staff|faculty|alumni|internal|external|current|new|featured|'
    r'category|categories|department|departments|division|divisions|location|locations|'
    r'campus|campuses|type|types|filter|filters|results?|page|pages|view|more)$', re.I)

# "staff-jobs", "faculty-jobs", "student-employment" -- a category, not a job.
_CATEGORY_SLUG = re.compile(
    r'^(?:[a-z]+-)*(?:staff|faculty|student|academic|adjunct|temporary|part-?time|'
    r'full-?time|hourly|professional|executive|administrative|research|teaching|'
    r'classified|union|internal|external)-(?:jobs?|positions?|openings?|employment|'
    r'opportunities|vacancies|careers?)$', re.I)


# Plenty of ATSs identify a posting in the QUERY rather than the path --
# Paycor's postings are all /career/JobIntroduction.action?clientId=..&id=..
# and Cornerstone's are ...?jobId=.. -- so "same path, different query"
# cannot by itself mean "filter link". An id parameter with a value marks a
# posting; a path that performs an action on one marks a bookmark or login.
_ID_QUERY = re.compile(r'(?:^|&)[a-z]*(?:job|posting|req|requisition|vacancy|position)?_?id=[^&=]+',
                       re.I)
_ACTION_PATH = re.compile(r'/(?:bookmarks?|login|log-?in|signin|sign-?in|apply|application|'
                          r'share|email|subscribe|alerts?|register|intro)(?:\.[a-z]+)?/?$', re.I)


def has_posting_id(url):
    return bool(_ID_QUERY.search(urlsplit(url).query))


def is_furniture(url, path, dominant_prefix, sibling_paths, careers_root):
    """Reasons a URL is a section of the site rather than one posting. Each
    returns a short label so the report can say WHY a row was dropped."""
    segs = [s for s in path.split('/') if s]

    if not segs:
        return 'site root'
    if url.rstrip('/') == (careers_root or '').rstrip('/'):
        return 'the careers link itself'

    if _ACTION_PATH.search(path):
        return f'action page (/{segs[-1]})'

    # A path that is the parent of other rows is usually a listing above
    # them -- unless it carries a posting id of its own, in which case the
    # children are that posting's own action links. Tufts' real posting
    # /jobs/23466 has /jobs/23466/login beneath it and was being dropped as
    # a "parent".
    kids = sum(1 for p in sibling_paths if p != path and p.startswith(path + '/'))
    if kids >= 2 and not re.search(r'\d{3,}', segs[-1]):
        return f'parent of {kids} other rows'

    last = segs[-1]
    if _NAV_SEGMENT.match(last):
        return f'section page (/{last})'
    if _CATEGORY_SLUG.match(last):
        return f'category page (/{last})'

    # Same path as other rows, differing only by query string: those are the
    # listing's own filter links ("?employment_type=Full time").
    return None


# A slug naming a role or a job document is a posting wherever it sits.
_JOB_SLUG_WORD = re.compile(
    r'job|position|vacanc|posting|professor|lecturer|instructor|faculty|fellow|'
    r'researcher|scientist|postdoc|dean|chair|coordinator|director|manager|analyst|'
    r'engineer|technician|nurse|adjunct|competition|requisition|opening', re.I)
_DOC_EXT = re.compile(r'\.(?:pdf|docx?|rtf)$', re.I)


def looks_like_posting(path, dominant_prefix, dominant_is_majority, listing_paths=(),
                       has_id_query=False):
    """A posting sits where this school's other postings sit. Once a clear
    majority of rows share one parent path, a row somewhere else is a
    section of the site, not a job -- Alaska's campus pages
    (/university-of-alaska-anchorage) have long hyphenated slugs and would
    otherwise pass for postings, while every real posting is under /jobs/.
    An explicit id still rescues a row from anywhere, since some sites do
    scatter postings across paths."""
    segs = [s for s in path.split('/') if s]
    if not segs:
        return False
    last = segs[-1]
    if re.search(r'\d{3,}', last):
        return True
    if dominant_prefix is not None and tuple(segs[:-1]) == dominant_prefix:
        return True

    # Three rescues from the path rule, each learned from a real miss:
    #   a job description filed as a PDF (Kuyper posts them under
    #   /wp-content/uploads/<year>/<month>/, so a posting from a different
    #   month reads as "off-path");
    #   a slug that names a role or competition (UPEI lists senior roles
    #   under their own path, apart from /hr/competition/<id>);
    #   a child of a page this same run judged to be a listing, since the
    #   things under a listing are its postings.
    if _DOC_EXT.search(last) or _JOB_SLUG_WORD.search(last):
        return True
    if has_id_query:
        return True
    parent = '/'.join([''] + segs[:-1])
    if parent in listing_paths:
        return True
    if dominant_is_majority:
        return False             # elsewhere on a site with a clear shape
    return last.count('-') >= 3


def clean_school(path_csv, careers_root=None):
    with open(path_csv, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    urls = [r['post_link'] for r in rows]
    if len(urls) < 3:
        return rows, []          # too few to infer a shape from; leave alone

    paths = {u: urlsplit(u).path.rstrip('/') or '/' for u in urls}
    path_list = list(paths.values())

    # The dominant template: the parent-segment tuple most rows share.
    prefix_counts = Counter(tuple([s for s in p.split('/') if s][:-1]) for p in path_list)
    dominant_prefix, dominant_n = (prefix_counts.most_common(1) or [((), 0)])[0]
    dominant_is_majority = dominant_n >= max(3, 0.5 * len(path_list))
    if dominant_n < 3:
        dominant_prefix = None
        dominant_is_majority = False

    # Rows sharing one path but differing by query are that listing's filters.
    by_path = defaultdict(list)
    for u in urls:
        by_path[paths[u]].append(u)

    # Pages that are parents of other rows are listings; their children are
    # therefore postings, which the off-path rule must not override.
    listing_paths = {p for p in path_list
                     if sum(1 for q in path_list if q != p and q.startswith(p + '/')) >= 2}

    kept, dropped = [], []
    for r in rows:
        u = r['post_link']
        p = paths[u]
        why = is_furniture(u, p, dominant_prefix, path_list, careers_root)
        if (why is None and len(by_path[p]) > 1 and urlsplit(u).query
                and not has_posting_id(u)):
            why = 'filter variant of a listing URL'
        if why is None and dominant_is_majority and not looks_like_posting(
                p, dominant_prefix, dominant_is_majority, listing_paths, has_posting_id(u)):
            why = 'outside this school\'s posting path'
        # No blanket rescue here: the verdicts above (site root, the careers
        # link, a parent of other rows, a named section, a category slug, a
        # filter variant) each identify furniture directly, and a rescue
        # applied to them undid correct calls -- "staff-jobs" contains the
        # word "jobs" and so read as a posting. The rescues live inside
        # looks_like_posting instead, where they gate ONLY the blunt
        # off-path rule that needs them.
        if why:
            dropped.append((u, why))
        else:
            kept.append(r)

    if not kept:                 # never empty a school on inference alone
        return rows, []

    # Losing almost everything does not mean the cleaning worked -- it means
    # the SCRAPER collected the wrong kind of page. Every CUNY campus is a
    # case in point: its file is 70 rows of cuny.jobs category listings
    # (/job-category/faculty/jobs/, /campus/<name>/jobs/) and no postings at
    # all, so "cleaning" it would leave one row and quietly hide that the
    # school has no data. Leave those files alone and report them, so they
    # reach the per-school fix queue instead of disappearing.
    if len(rows) >= 10 and len(kept) < 0.2 * len(rows):
        return rows, [('__NEEDS_SCRAPER_FIX__',
                       f'would drop {len(dropped)} of {len(rows)} rows -- '
                       f'scraper is collecting listing pages, not postings')]
    return kept, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--school', default='', help='one school_id')
    ap.add_argument('--report', default='')
    args = ap.parse_args()

    careers = {}
    master = os.path.join(HERE, 'schools_master.csv')
    if os.path.exists(master):
        with open(master, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                careers[r['school_id']] = r['careers_link']

    pattern = (f'school_id_{args.school}_job_posts.csv' if args.school
               else 'school_id_*_job_posts.csv')
    files = sorted(glob.glob(os.path.join(POSTS_DIR, pattern)))

    total_before = total_after = 0
    reasons = Counter()
    report_rows = []
    touched = 0
    for path_csv in files:
        sid = os.path.basename(path_csv).split('_')[2]
        kept, dropped = clean_school(path_csv, careers.get(sid))
        before = len(kept) + len(dropped)
        total_before += before
        total_after += len(kept)
        if dropped:
            touched += 1
            for u, why in dropped:
                reasons[why.split('(')[0].strip()] += 1
                report_rows.append({'school_id': sid, 'dropped_url': u, 'reason': why})
        if dropped and not args.dry_run:
            with open(path_csv, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=['school_id', 'post_link'])
                w.writeheader()
                w.writerows(kept)

    print(f'{"DRY RUN -- " if args.dry_run else ""}{len(files)} files, '
          f'{touched} would change' if args.dry_run else
          f'{len(files)} files, {touched} changed')
    print(f'  rows {total_before} -> {total_after}  ({total_before - total_after} removed)')
    for why, n in reasons.most_common():
        print(f'    {n:6d}  {why}')

    if args.report and report_rows:
        with open(args.report, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['school_id', 'dropped_url', 'reason'])
            w.writeheader()
            w.writerows(report_rows)
        print(f'  wrote {args.report}')


if __name__ == '__main__':
    main()
