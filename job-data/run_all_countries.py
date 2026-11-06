"""
Runs one scraper stage across every country in schools_master.

Run from job-data/:
    python3 run_all_countries.py --stage postings --redo --timeout 300
    python3 run_all_countries.py --stage info --timeout 900

run_school_scrapers.py takes a single country, and several of ours have
spaces in the name ("United Kingdom", "New Zealand", "Hong Kong"). Looping
over them in shell means quoting them correctly every time; doing it here
removes that class of bug from the weekly script.
"""
import argparse
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onedrive_io  # noqa: F401  (retry OneDrive's sync locks)
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def countries():
    seen = []
    with open(os.path.join(HERE, 'schools_master.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            c = (row.get('country') or '').strip()
            if c and c not in seen:
                seen.append(c)
    # US first: it is the bulk of the set, so a run that is cut short still
    # covers the most ground.
    seen.sort(key=lambda c: (c != 'US', c))
    return seen


def _failed_ids(country, stage, workers):
    log_dir = os.path.expanduser('~/Library/Logs/faculty-job-atlas/run_logs')
    ids = []
    for k in range(workers):
        path = os.path.join(log_dir, f'run_log_{country}_{stage}_shard{k}of{workers}.csv')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                ids += [r['school_id'] for r in csv.DictReader(f) if r['status'] != 'complete']
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['postings', 'info'], required=True)
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--redo', action='store_true')
    ap.add_argument('--only')
    ap.add_argument('--workers', type=int, default=1,
                    help='split each country across this many parallel processes')
    args = ap.parse_args()

    targets = [args.only] if args.only else countries()
    print(f'{args.stage}: {len(targets)} countries', flush=True)
    failed = []
    for i, country in enumerate(targets, 1):
        cmd = [sys.executable, os.path.join(HERE, 'run_school_scrapers.py'), country,
               '--stage', args.stage, '--timeout', str(args.timeout)]
        if args.redo:
            cmd.append('--redo')
        print(f'\n=== [{i}/{len(targets)}] {country} ===', flush=True)
        try:
            # One process per shard, each with its own browser. Reading one
            # school at a time took 5 hours for 265 US schools on 2026-11-05
            # (a backlog of ~5,000 unread jobs); the schools are independent.
            procs = [subprocess.Popen(cmd + (['--shard', f'{k}/{args.workers}']
                                             if args.workers > 1 else []), cwd=HERE)
                     for k in range(args.workers)]
            codes = [p.wait() for p in procs]
            if any(codes):
                failed.append(country)
            retry = _failed_ids(country, args.stage, args.workers) if args.workers > 1 else []
            if retry:
                # Oracle boards time out when several sessions hit them at
                # once (11 schools on 2026-11-06) and all read fine alone.
                print(f'  retrying {len(retry)} failed schools one at a time', flush=True)
                subprocess.run(cmd + ['--ids', ','.join(retry)], cwd=HERE)
        except Exception as e:
            print(f'  {country}: {type(e).__name__}: {e}', flush=True)
            failed.append(country)
    if failed:
        print(f'\ncountries that exited non-zero: {failed}', flush=True)
    print(f'{args.stage} pass finished', flush=True)


if __name__ == '__main__':
    main()
