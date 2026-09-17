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
checkpoint of postings it has already read, so it only fetches URLs it has
not seen before.

That only holds because the info stage (step 4) runs with `--redo`. Without
it, the runner
skips any school whose info checkpoint says `complete` -- every school
after its first run -- so new postings were scraped but never fetched and
never reached the map. By 2026-09-14 that had silently left 17,183 links
off the map, including open faculty posts at Cambridge, NUS and HKU.
`--redo` does not refetch what is cached; it only stops the skip.

## What it does, and why in this order

1. **postings** - re-scrape each school's listing for links
2. **clean** - strip furniture from the link sets *and their checkpoints*
3. **mathjobs** - pull mathjobs.org, the only place many mathematics,
   statistics and operations research faculty posts are advertised
4. **info** - fetch detail for newly seen postings only
5. **prune** - drop info rows whose URL is no longer in the posts CSV
6. **build** - rebuild `postings.json`, stamp first-seen dates
7. **publish** - commit and push

Clean must come before info. `job_info` reads its link list from the
`job_postings` checkpoint, not from the posts CSV, so cleaning afterwards
would leave the furniture in play for another week. That exact ordering
mistake is why Bowdoin's Atom feeds kept reappearing on the map.

## MathJobs

`mathjobs_source.py` (stage 3) adds mathjobs.org, where most mathematics,
statistics and operations research faculty jobs are advertised. Many
departments post there and nowhere else: Tufts' applied mathematics
assistant professorship never appears on jobs.tufts.edu, and before this
stage existed the corpus held **zero** mathjobs links.

It costs **one HTTP request**. The deadline-sorted listing returns every
open position (604 on 2026-09-16) with institution, title and deadline
inline, so no position page is fetched. That matters: mathjobs' robots.txt
sets `Crawl-delay: 5`, and fetching 604 detail pages would be 50 minutes of
crawling every night. Detail rows are filled in from the listing, so the
info stage finds nothing left to fetch for these postings.

It runs **after clean and before info**. Run before cleaning, every mathjobs
link would be dropped as "outside this school's posting path" -- a school's
own site is always its dominant prefix -- which is also why
`clean_job_posts.py` exempts `mathjobs.org/jobs/list/<id>` explicitly.

**Matching schools is the fiddly part, and it is exact on purpose.**
`schools_master.csv` uses IPEDS-style campus names ("Purdue
University-Main Campus") while mathjobs writes "Purdue University,
Mathematics". Two looser rules were tried and both put real postings in the
wrong place:

* Keying on the text before the first comma added **17 duplicate schools**
  and filed every Cal State campus under Bakersfield.
* Accepting any school whose words were a *subset* of the employer's filed
  **23 positions under the wrong university** -- Central China Normal
  University under Central College (Iowa), Virginia Tech under the
  University of Virginia, Duke Kunshan under Duke, and Jane Street Capital
  under Capital University.

An institution's distinguishing words must now **equal** a school's, tried
on the institution alone and then institution + campus. That places 526 of
604 positions.

**It never adds a school.** The other 44 institutions go to
`refresh_logs/mathjobs_review_<date>.csv` and are otherwise ignored, because
an unmatched employer is as often an alias of a school already in the list
(Virginia Tech, Humboldt-Universität zu Berlin) as a genuinely new
institution (New Uzbekistan University), and that judgement belongs to a
person.

An earlier version did register them automatically. It added duplicates of
schools already present under their campus names, admitted trading firms as
"schools", and geocoded four Korean universities into Moldova -- mathjobs
writes "Korea, The Republic of", which a geocoder resolves to Transnistria.
All of that was removed.

```bash
python3 mathjobs_source.py --dry-run        # report, write nothing
```

## Seeing what is new

`job-data/posting_first_seen.csv` records the date each posting URL was
first observed. It is the only record of that -- once a posting has been
scraped it looks identical to one that has been up for months, so this
cannot be reconstructed later. Do not delete it.

The map has a **First seen** dropdown under Availability: "found in the
latest refresh" (its label carries that run's date), last 7 days, or last 30
days. It replaced a single checkbox that showed everything found since
tracking began, which could not tell one run's finds from the next.

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
