"""
Switches inline-listing schools over to section-based scraping.

Run from job-data/:
    python3 apply_inline_listing.py --probe /tmp/inline_probe.json --dry-run
    python3 apply_inline_listing.py --probe /tmp/inline_probe.json

WHY THESE SCHOOLS NEEDED THEIR OWN SHAPE
The pipeline assumes one posting is one URL. A run of schools breaks that:
they write each opening as a SECTION of a single page, with nothing to
click through to. Dubuque publishes 24 openings that way, St Thomas
Aquinas 2, Whittier 1. Every link-based scraper we have returns 0 or 3
rows on those pages -- not because the fetch failed, but because there is
no per-job href in the HTML to find.

So the postings side mints a pseudo-URL per section (listing page + a
#slug of that section's heading) and the info side resolves the fragment
back to that section's own text. Skipping the fragment would give all 24
Dubuque postings the same title and the same 117KB description.

Only schools where the extractor actually found sections are rewritten;
a school it found nothing on keeps whatever scraper it has, since an
empty rewrite would trade a working-but-quiet scraper for a broken one.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_CODE = os.path.join(HERE, 'school_job_posts_code')
INFO_CODE = os.path.join(HERE, 'school_job_info_code')

FIND_LINKS = '''def find_links():
    """CUSTOMIZED: this school writes each opening as a SECTION of its
    careers page -- there is no per-job link to collect, which is why every
    link-based scraper returned {had} row(s) against {found} real openings
    on the page.

    Each section becomes CAREERS_LINK + '#' + a slug of its own heading,
    and school_id_{sid}_job_info.py resolves that fragment back to the
    section's text."""
    return lib.scrape_inline_listing(CAREERS_LINK)
'''

FETCH_DETAIL = '''def fetch_detail(url):
    """CUSTOMIZED: postings here are sections of one page, addressed as
    CAREERS_LINK#<slug>. Resolves the fragment back to that section alone
    -- the generic reader would hand every posting the whole page."""
    return jinfo.fetch_detail_inline(url)
'''


def swap(path, marker, replacement, end_marker):
    if not os.path.exists(path):
        return 'missing'
    with open(path, encoding='utf-8') as f:
        src = f.read()
    start, end = src.find(marker), src.find(end_marker)
    if start == -1 or end == -1 or end < start:
        return 'no-anchor'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src[:start] + replacement + '\n\n' + src[end:])
    return 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', default='/tmp/inline_probe.json')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--min-sections', type=int, default=1)
    args = ap.parse_args()

    probe = json.load(open(args.probe))
    targets = [r for r in probe if r['sections'] >= args.min_sections]
    skipped = [r for r in probe if r['sections'] < args.min_sections]

    print(f'{len(targets)} schools have inline sections ({sum(r["sections"] for r in targets)} '
          f'postings); {len(skipped)} found none and are left alone')
    if args.dry_run:
        for r in targets:
            print(f'  [{r["school_id"]:>5}] {r["sections"]:>3}  {r["name"][:38]}')
        return

    done = 0
    for r in targets:
        sid = r['school_id']
        a = swap(os.path.join(POSTS_CODE, f'school_id_{sid}_job_postings.py'),
                 'def find_links():',
                 FIND_LINKS.format(sid=sid, had=0, found=r['sections']),
                 'def main():')
        b = swap(os.path.join(INFO_CODE, f'school_id_{sid}_job_info.py'),
                 'def fetch_detail(url):', FETCH_DETAIL, 'def main():')
        if a == 'ok' and b == 'ok':
            done += 1
        else:
            print(f'  [{sid}] postings={a} info={b}')
    print(f'rewrote {done}/{len(targets)} school script pairs')


if __name__ == '__main__':
    main()
