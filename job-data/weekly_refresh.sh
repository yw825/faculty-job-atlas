#!/bin/bash
# Weekly full refresh of the Faculty Job Atlas.
#
# Run by launchd (see com.facultyjobatlas.weekly.plist) or by hand:
#     bash job-data/weekly_refresh.sh
#
# Stages, in the order that matters:
#   1. postings   re-scrape every school's listing -> new posting links
#   2. clean      strip furniture from the link sets AND their checkpoints
#   3. info       fetch detail; the checkpoint means only NEW links are paid
#                 for, so this stays cheap after the first run
#   4. prune      drop info rows whose URL is no longer in the posts CSV
#   5. build      rebuild postings.json and stamp first-seen dates
#   6. publish    commit and push
#
# Clean must come BEFORE info: job_info reads its link list from the
# job_postings checkpoint, so cleaning after would leave the furniture in
# play for another week. That ordering is why Bowdoin's Atom feeds kept
# coming back.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/job-data" || exit 1

LOGDIR="$ROOT/job-data/refresh_logs"
mkdir -p "$LOGDIR"
STAMP="$(date +%Y-%m-%d)"
LOG="$LOGDIR/refresh_$STAMP.log"
exec >>"$LOG" 2>&1

echo "=============================================================="
echo "refresh started $(date)"
echo "=============================================================="

say(){ echo; echo "--- $* ($(date +%H:%M:%S)) ---"; }

say "1/6 postings"
python3 run_all_countries.py --stage postings --redo --timeout 300

say "2/6 clean furniture from link sets and checkpoints"
python3 clean_job_posts.py --report "cleaning_report_$STAMP.csv" | head -20

say "3/6 info (only newly seen postings are fetched)"
python3 run_all_countries.py --stage info --timeout 900

say "4/6 prune stale info rows"
python3 prune_stale_info.py | head -5

say "5/6 rebuild map"
python3 build_map_data.py | tail -8

say "6/6 publish"
cd "$ROOT" || exit 1
if [ -n "$(git status --porcelain)" ]; then
  NEW=$(python3 -c "
import json
d=json.load(open('postings.json'))
print(d.get('first_seen_new', 0))
")
  git add -A
  git commit -q -m "Weekly refresh $STAMP: $NEW new postings

Automated run of job-data/weekly_refresh.sh.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
  if git push -q origin main; then
    echo "pushed; $NEW new postings this week"
  else
    echo "PUSH FAILED -- committed locally, resolve by hand"
  fi
else
  echo "no changes to publish"
fi

echo
echo "refresh finished $(date)"
# Keep the last 12 weeks of logs.
ls -1t "$LOGDIR"/refresh_*.log 2>/dev/null | tail -n +13 | xargs -r rm -f
