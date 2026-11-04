"""
Drops job_info rows whose posting URL is no longer in the school's
job_posts.csv.

Run from job-data/:
    python3 prune_stale_info.py --dry-run
    python3 prune_stale_info.py

WHY THESE ROWS EXIST
job_info reads its URL list from the job_postings CHECKPOINT, not from
job_posts.csv. When clean_job_posts.py removed careers-site furniture from
the CSVs -- and when a later re-scrape replaced a school's link set -- the
info CSVs kept their old rows. Nothing re-derived them, so they survived
into postings.json.

The rows are not merely redundant; they are the worst kind of row in the
map, because each one is a page that is not a job. Bowdoin surfaced this:
its map entries included

    https://careers.bowdoin.edu/postings/all_jobs.atom
    https://careers.bowdoin.edu/postings/search.atom?...

both titled "Bowdoin College: All Jobs", both an Atom FEED that opens as
raw XML rather than a posting. Alongside them sat 16 /bookmarks?posting_id=
links, which are the "save this job" action rather than the job.

job_posts.csv is the cleaned, authoritative link set, so it is the filter.
A school whose posts CSV is empty is skipped rather than emptied, since
that would delete rows on the strength of a failed scrape.
"""
import argparse
import csv
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(HERE, 'school_job_posts')
INFO = os.path.join(HERE, 'school_job_info')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    total_removed = touched = skipped = 0
    samples = []
    for path in sorted(glob.glob(os.path.join(INFO, '*_job_info.csv'))):
        school_id = os.path.basename(path).split('_')[2]
        posts_path = os.path.join(POSTS, f'school_id_{school_id}_job_posts.csv')
        if not os.path.exists(posts_path):
            continue
        try:
            with open(posts_path, encoding='utf-8') as f:
                keep = {r['post_link'] for r in csv.DictReader(f) if r.get('post_link')}
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fields = reader.fieldnames
                rows = list(reader)
        except Exception:
            continue
        if not rows or not keep:
            skipped += 1 if rows and not keep else 0
            continue

        kept = [r for r in rows if r.get('posting_url') in keep]
        removed = len(rows) - len(kept)
        if not removed:
            continue
        # A prune that would empty the school is a signal that the two files
        # disagree wholesale (a re-scrape that changed every URL), not that
        # every row is furniture -- leave it and report instead.
        if not kept:
            skipped += 1
            continue
        total_removed += removed
        touched += 1
        for r in rows:
            if r.get('posting_url') not in keep and len(samples) < 10:
                samples.append((school_id, r.get('job_title_in_post', '')[:40],
                                r.get('posting_url', '')[:70]))
        if not args.dry_run:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(kept)

    verb = 'would remove' if args.dry_run else 'removed'
    print(f'{verb} {total_removed} stale rows across {touched} schools '
          f'({skipped} skipped: pruning would have emptied them)')
    for sid, title, url in samples:
        print(f'  [{sid}] {title:42s} {url}')


if __name__ == '__main__':
    main()
