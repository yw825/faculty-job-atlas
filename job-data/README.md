# Faculty job-openings database (work in progress)

## Files

- **schools_master.csv** — all 1,867 schools from the site's existing dataset
  (school_id, name, country, base_url), plus `careers_link` /
  `ats_platform` / `confidence` / `notes` columns. 68 schools already have a
  careers link filled in (New Zealand, Macau, Singapore, Hong Kong, and part
  of Canada) from an earlier search-based pass. The rest are blank, waiting
  for `find_faculty_job_links.py` to fill them in.

- **find_faculty_job_links.py** — the crawler. Pure Python (requests +
  BeautifulSoup, with a Playwright headless-browser fallback for sites that
  block plain HTTP requests) — no Claude/API calls, free to run as much as
  you want.

## Setup (one time)

```bash
pip install requests beautifulsoup4 playwright
playwright install chromium
```

## Running it

```bash
cd job-data
python3 find_faculty_job_links.py
```

- Skips any row that already has a `careers_link`, so it's safe to stop
  (Ctrl-C) and re-run anytime — it picks up where it left off.
- Saves a checkpoint back to `schools_master.csv` every 50 schools
  processed.
- `--limit N` processes only the next N unfilled schools, useful for a
  quick test run before committing to the full ~1,800 remaining.

## How it decides on a link

1. Fetches the school's homepage, looks at every link, and scores it by
   keyword (careers, jobs, vacancies, "work at ___", faculty/academic
   position, etc.) — plus a big bonus if the link points at a *known* job
   platform domain (Workday, Taleo, SmartRecruiters, PageUp, iCIMS,
   SuccessFactors, and others — see `ATS_DOMAINS` in the script).
2. If the best match on the homepage is a generic "Careers" hub page (not
   already a known platform), it follows that link one more hop and looks
   there too — schools often link to an internal hub page that itself links
   out to the real ATS portal.
3. `confidence` is `high` when the final link is a recognized ATS platform,
   `medium` when it's a plausible page found by keyword match only, and
   `not_found` when nothing usable turned up.

## Known limitations

This is a heuristic, not a verified list — expect some wrong or missing
links, especially:
- Schools whose site heavily blocks bots even from a real browser.
- Schools whose homepage doesn't link directly to their careers page (needs
  more than one hop, or isn't discoverable from the homepage at all).
- `medium`-confidence links may be a hub/about page rather than the live
  listings themselves.

A slower but more accurate alternative (used for the schools already filled
in) is a web search per school rather than crawling the homepage — it found
the *actual* ATS portal directly in cases where the homepage crawl missed
it. Worth spot-checking `medium`/`not_found` rows against a search
eventually.
