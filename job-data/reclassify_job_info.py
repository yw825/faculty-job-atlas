"""Re-apply the current rank and date rules to every job-info CSV row, from
the advert text the info checkpoints already keep -- no board is re-read.

Only position_type, deadline_of_application, posted_date and
position_start_date are rewritten; title, department, keywords and job term
stay as they are. Run it after changing rank_classifier.py or the date
extractors in job_info_lib.py, then rebuild the map.

    python3 reclassify_job_info.py            # every tracked CSV
    python3 reclassify_job_info.py 1018 1790  # just these schools
"""
import csv
import json
import os
import subprocess
import sys
from collections import Counter

import job_info_lib as jl
from rank_classifier import classify_rank

HERE = os.path.dirname(os.path.abspath(__file__))
UPDATED = ('position_type', 'deadline_of_application', 'posted_date', 'position_start_date')


def tracked_csvs():
    # OneDrive restores deleted CSVs of removed schools as untracked files;
    # only the ones git tracks are live.
    out = subprocess.run(['git', 'ls-files', 'school_job_info/*.csv'], cwd=HERE,
                         capture_output=True, text=True, check=True).stdout
    return [os.path.join(HERE, p) for p in out.split()]


def reclassify(path, changes):
    sid = int(os.path.basename(path).split('_')[2])
    country = jl.school_country(sid)
    try:
        with open(os.path.join(jl.HERE, 'school_job_info_code', f'school_id_{sid}_job_info.checkpoint'),
                  encoding='utf-8') as f:
            raw = json.load(f).get('raw') or {}
    except (OSError, ValueError):
        raw = {}
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        entry = raw.get(row.get('posting_url', ''))
        advert = entry.get('description', '') if isinstance(entry, dict) and 'error' not in entry else ''
        title = row.get('job_title_in_post', '')
        new = {'position_type': '; '.join(classify_rank(title, advert, country))}
        if advert:
            new['deadline_of_application'], new['posted_date'], new['position_start_date'] = \
                jl.classify_dates(advert, country)
        for k, v in new.items():
            if (row.get(k) or '') != v:
                changes[k] += 1
                row[k] = v
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=jl.FIELDS, extrasaction='ignore', restval='')
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    paths = tracked_csvs()
    if len(sys.argv) > 1:
        wanted = {f'school_id_{a}_job_info.csv' for a in sys.argv[1:]}
        paths = [p for p in paths if os.path.basename(p) in wanted]
    changes = Counter()
    n_rows = 0
    for i, path in enumerate(paths, 1):
        n_rows += reclassify(path, changes)
        if i % 200 == 0:
            print(f'  {i}/{len(paths)} files', flush=True)
    print(f'{len(paths)} files, {n_rows} rows; changed: ' +
          ', '.join(f'{k} {changes[k]}' for k in UPDATED))


if __name__ == '__main__':
    main()
