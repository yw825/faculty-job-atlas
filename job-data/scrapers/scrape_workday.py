"""
Scrapes individual faculty job postings from Workday-hosted career sites
using Workday's public CXS (Candidate Experience Site) JSON API -- no
auth, no browser needed.

URL shape: https://{tenant}.wd{N}.myworkdayjobs.com/{site}...
API:       POST https://{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
"""
import re
import time
import requests

WORKDAY_URL_RE = re.compile(
    r"https?://(?P<tenant>[\w-]+)\.(?P<wd>wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?(?P<site>[^/?]+)"
)

FACULTY_TITLE_RE = re.compile(
    r"\b(professor|lecturer|instructor|faculty|postdoc|post-doctoral|"
    r"teaching\s+(fellow|associate)|research\s+scientist)\b", re.I
)

HEADERS = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}


def parse_workday_url(careers_link):
    m = WORKDAY_URL_RE.search(careers_link)
    if not m:
        return None
    return m.group("tenant"), m.group("wd"), m.group("site")


def fetch_postings(careers_link, school_name, limit_pages=5, page_size=20, timeout=15):
    parsed = parse_workday_url(careers_link)
    if not parsed:
        return [], "URL_NOT_WORKDAY_SHAPE"
    tenant, wd, site = parsed
    api = f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    base_site = f"https://{tenant}.{wd}.myworkdayjobs.com/{site}"

    postings = []
    offset = 0
    for _ in range(limit_pages):
        try:
            resp = requests.post(
                api, headers=HEADERS, timeout=timeout,
                json={"appliedFacets": {}, "limit": page_size, "offset": offset, "searchText": ""},
            )
            if resp.status_code != 200:
                return postings, f"HTTP_{resp.status_code}"
            data = resp.json()
        except Exception as e:
            return postings, f"ERROR:{type(e).__name__}"

        jobs = data.get("jobPostings", [])
        if not jobs:
            break
        for j in jobs:
            title = j.get("title", "")
            if not FACULTY_TITLE_RE.search(title):
                continue
            postings.append({
                "school": school_name,
                "title": title,
                "location": j.get("locationsText", ""),
                "posted": j.get("postedOn", ""),
                "url": base_site + j.get("externalPath", ""),
                "platform": "Workday",
            })
        offset += page_size
        if offset >= data.get("total", 0):
            break
        time.sleep(0.2)
    return postings, "OK"


if __name__ == "__main__":
    import csv, json, sys
    from concurrent.futures import ThreadPoolExecutor, as_completed

    CSV_PATH = "/Users/yusiwei/Downloads/My fun/faculty-job-atlas/job-data/schools_master.csv"
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    workday_rows = [r for r in rows if r["ats_platform"] == "Workday" and "myworkdayjobs.com" in r["careers_link"]]
    print(f"{len(workday_rows)} Workday schools to scrape")

    all_postings = []
    errors = []
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = {ex.submit(fetch_postings, r["careers_link"], r["name"]): r for r in workday_rows}
        for i, fut in enumerate(as_completed(futures), 1):
            r = futures[fut]
            postings, status = fut.result()
            all_postings.extend(postings)
            if status != "OK":
                errors.append((r["name"], status))
            if i % 20 == 0:
                print(f"  {i}/{len(workday_rows)} schools done, {len(all_postings)} faculty postings so far")

    print(f"\nDone. {len(all_postings)} faculty postings from {len(workday_rows)-len(errors)} schools ({len(errors)} errors).")
    if errors:
        print("Errors:", errors[:20])

    out_path = "/Users/yusiwei/Downloads/My fun/faculty-job-atlas/job-data/jobs_workday.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_postings, f, indent=2)
    print("Saved to", out_path)
