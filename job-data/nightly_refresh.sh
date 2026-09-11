#!/bin/bash
# Nightly full refresh of the Faculty Job Atlas.
#
# Run by launchd (see com.facultyjobatlas.nightly.plist) or by hand:
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

# launchd runs with a minimal PATH, where "python3" is /usr/bin/python3 --
# the SYSTEM interpreter, which has none of this project's dependencies
# (bs4, playwright, requests, pypdf all live in the pyenv install). A job
# that resolved python3 from PATH would fail on its first import, weekly,
# silently. The interpreter is therefore pinned to an absolute path,
# written in at install time, and checked before any work starts.
PYTHON="/Users/yusiwei/.pyenv/versions/3.10.14/bin/python3"

if [ ! -x "$PYTHON" ]; then
  echo "FATAL: interpreter $PYTHON not found. Re-run setup_refresh.sh." >&2
  exit 1
fi

# A nightly cadence can overlap: if one pass runs long, the next fires
# while it is still going, and two scrapers writing the same checkpoints
# would corrupt them. The lock makes a second start exit immediately.
LOCK="$ROOT/job-data/.refresh.lock"
if [ -e "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "refresh already running (pid $(cat "$LOCK")); exiting" >&2
  exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

LOGDIR="$ROOT/job-data/refresh_logs"
mkdir -p "$LOGDIR"
STAMP="$(date +%Y-%m-%d)"
LOG="$LOGDIR/refresh_$STAMP.log"
exec >>"$LOG" 2>&1

echo "=============================================================="
echo "refresh started $(date)"
echo "=============================================================="

say(){ echo; echo "--- $* ($(date +%H:%M:%S)) ---"; }

if ! "$PYTHON" -c "import bs4, playwright, requests" 2>/dev/null; then
  echo "FATAL: $PYTHON is missing dependencies (bs4/playwright/requests)." >&2
  exit 1
fi

say "1/6 postings"
"$PYTHON" run_all_countries.py --stage postings --redo --timeout 300

say "2/6 clean furniture from link sets and checkpoints"
"$PYTHON" clean_job_posts.py --report "cleaning_report_$STAMP.csv" | head -20

say "3/6 info (only newly seen postings are fetched)"
"$PYTHON" run_all_countries.py --stage info --timeout 900

say "4/6 prune stale info rows"
"$PYTHON" prune_stale_info.py | head -5

say "5/6 rebuild map"
"$PYTHON" build_map_data.py | tail -8

say "6/6 publish"
cd "$ROOT" || exit 1
if [ -n "$(git status --porcelain)" ]; then
  NEW=$("$PYTHON" -c "
import json
d=json.load(open('postings.json'))
print(d.get('first_seen_new', 0))
")
  git add -A
  git commit -q -m "Nightly refresh $STAMP: $NEW new postings

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
