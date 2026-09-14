# Nightly refresh

Re-scrapes every school, finds new postings, rebuilds the map and pushes.

Runs **every day at 09:00**. A full pass takes roughly 4-6 hours, so the
map is current by early afternoon.

It runs in the daytime on purpose: this is a laptop, and a closed lid puts
it to sleep regardless of any setting. The script runs `caffeinate` for its
whole duration, so the Mac will not idle-sleep mid-run while the lid is
open. If the lid is closed mid-run, the pass is suspended and carries on
when the Mac wakes -- nothing is corrupted, the map is just later.

## Install the schedule (once)

```bash
cp job-data/com.facultyjobatlas.nightly.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.facultyjobatlas.nightly.plist
```

If the Mac is asleep or closed at 09:00, launchd runs the job as soon as the
machine is next awake rather than skipping the day. No scheduled wake
(`pmset repeat`) is needed.

Only one pass runs at a time: a lock file makes a second start exit
immediately, so a run that goes long cannot be overlapped by the next
night's firing and corrupt the checkpoints both would write.

Check it is registered:

```bash
launchctl list | grep facultyjobatlas
```

Stop it:

```bash
launchctl unload ~/Library/LaunchAgents/com.facultyjobatlas.nightly.plist
```

## Run it by hand

```bash
bash job-data/nightly_refresh.sh          # same thing, right now
tail -f job-data/refresh_logs/refresh_$(date +%F).log
```

Expect **4-6 hours**. Most of it is the postings stage, which visits every
school. The detail stage is cheap after the first run: `job_info` keeps a
checkpoint of postings it has already read, so it only fetches URLs that
are new this week.

## What it does, and why in this order

1. **postings** - re-scrape each school's listing for links
2. **clean** - strip furniture from the link sets *and their checkpoints*
3. **info** - fetch detail for newly seen postings only
4. **prune** - drop info rows whose URL is no longer in the posts CSV
5. **build** - rebuild `postings.json`, stamp first-seen dates
6. **publish** - commit and push

Step 2 must come before step 3. `job_info` reads its link list from the
`job_postings` checkpoint, not from the posts CSV, so cleaning afterwards
would leave the furniture in play for another week. That exact ordering
mistake is why Bowdoin's Atom feeds kept reappearing on the map.

## Seeing what is new

`job-data/posting_first_seen.csv` records the date each posting URL was
first observed. It is the only record of that -- once a posting has been
scraped it looks identical to one that has been up for months, so this
cannot be reconstructed later. Do not delete it.

The map has a **"New since last refresh"** checkbox under Availability --
with a nightly cadence that means "found last night".

The first run set every posting's date to the same day. Those are not new,
we simply had no record before, so the earliest date in the ledger is
treated as a baseline and postings bearing it are never counted as new.
The first genuinely new postings will appear after the next refresh.

## Checking a run

```bash
grep -E "^---|new postings|pushed|FAILED" job-data/refresh_logs/refresh_*.log | tail -20
```

The commit message carries the count: `Nightly refresh 2026-09-14: 137 new postings`.

If the push fails the run still commits locally, and says so, so nothing
is lost -- resolve it by hand and push.

The last 12 logs are kept; older ones are deleted automatically.

## If Python moves

`nightly_refresh.sh` calls an **absolute** interpreter path, currently:

```
/Users/yusiwei/.pyenv/versions/3.10.14/bin/python3
```

This is deliberate. launchd runs with a minimal PATH where `python3` is
`/usr/bin/python3` -- the system interpreter, which has none of this
project's dependencies. A job that resolved `python3` from PATH would fail
on its first import, weekly, in silence.

If you upgrade or move Python, edit the `PYTHON=` line at the top of
`nightly_refresh.sh`. The script refuses to start if that path is gone, and
checks `bs4`/`playwright`/`requests` import before doing any work, so a
broken interpreter fails loudly in the log's first lines rather than
halfway through a scrape.

## Does it actually publish?

Yes -- verified, not assumed. A real `git push` was run from a stripped
environment (`env -i`, minimal PATH, no interactive shell) and succeeded:
the osxkeychain credential helper serves the GitHub credential without a
login session. Note that `git push --dry-run` is NOT a valid test here --
this repo is public, so ref discovery succeeds without any credential at
all and reports "Everything up-to-date" whether auth works or not.

If a push ever does fail, the run still commits locally and the log says
`PUSH FAILED -- committed locally, resolve by hand`, so no work is lost.
