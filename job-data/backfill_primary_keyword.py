"""
Recomputes the TITLE-derived part of area_key_words across every school's
job_info CSV, in place, without re-scraping anything.

Run from job-data/:
    python3 backfill_primary_keyword.py --dry-run
    python3 backfill_primary_keyword.py

WHY THIS CAN BE DONE OFFLINE
area_key_words has three parts: the subject named in the title, plus
topics read out of the description's research and teaching sentences. The
description isn't stored in the CSV, so those two parts can only be
rebuilt by re-fetching every posting. The title IS stored -- so when
extract_primary_keyword improves, the subject can be recovered for all
~30k rows from the file alone.

The improvements this backfills are titles that name the field somewhere
other than an "in/of" clause: before the rank ("Tenure Track Political
Science Professor"), after a dash ("Adjunct Instructor - English"), or
across a colon ("Psychology: Adjunct Position"). Those returned nothing
before, which left the postings unfindable by the map's subject search.

Only ADDS a missing subject -- never removes or reorders what's there, so
a re-run is a no-op and description-derived topics are left untouched.
"""
import argparse
import csv
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import job_info_lib as jinfo

INFO_DIR = os.path.join(HERE, 'school_job_info')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(INFO_DIR, '*_job_info.csv')))
    changed_rows = changed_files = 0
    samples = []
    for path in files:
        try:
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fields = reader.fieldnames
                rows = list(reader)
        except Exception:
            continue
        if not rows or 'area_key_words' not in (fields or []):
            continue
        dirty = False
        for r in rows:
            title = (r.get('job_title_in_post') or '').strip()
            if not title:
                continue
            subject = jinfo.extract_primary_keyword(title)
            if not subject:
                continue
            existing = r.get('area_key_words') or ''
            if subject.lower() in existing.lower():
                continue
            r['area_key_words'] = f'{subject}; {existing}'.strip('; ') if existing else subject
            dirty = True
            changed_rows += 1
            if len(samples) < 12:
                samples.append((subject, title[:52]))
        if dirty:
            changed_files += 1
            if not args.dry_run:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)

    print(f'{"would add" if args.dry_run else "added"} a title subject to '
          f'{changed_rows} rows across {changed_files} of {len(files)} school files')
    for subj, title in samples:
        print(f'  +{subj:36s} <- {title}')


if __name__ == '__main__':
    main()
