"""
Finds each university's faculty/academic job-openings page and saves the
results to CSV. Runs entirely locally (requests + BeautifulSoup, with a
Playwright headless-browser fallback for sites that block plain HTTP
requests) -- no Claude/API calls, no tokens, free to re-run as much as you
want.

SETUP (one time):
    pip install requests beautifulsoup4 playwright
    playwright install chromium

USAGE:
    python3 find_faculty_job_links.py

    Reads schools_master.csv (school_id, name, country, base_url,
    careers_link, ats_platform, confidence, notes), skips any row that
    already has a careers_link filled in, and fills in the rest. Saves a
    checkpoint back to schools_master.csv after every 50 schools processed,
    so you can Ctrl-C at any time and just re-run later to pick up where you
    left off.

    Optional: python3 find_faculty_job_links.py --limit 100
    to only process the next 100 unfilled schools (useful for testing).
"""
import argparse
import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CSV_PATH = "schools_master.csv"
FIELDNAMES = ["school_id", "name", "country", "base_url", "careers_link",
              "ats_platform", "confidence", "notes"]

CHUNK_SIZE = 50
REQUESTS_WORKERS = 25
PLAYWRIGHT_CONCURRENCY = 6

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Known third-party ATS/job platforms. A link pointing at one of these
# domains is a very strong signal it's the *real* job-listings page, even if
# the link text/URL on the school's own homepage doesn't say "careers" --
# e.g. a school's homepage might just say "Work with us" and link out to
# jobs.smartrecruiters.com/TheUniversity, which this catches directly.
ATS_DOMAINS = {
    "smartrecruiters.com": "SmartRecruiters",
    "taleo.net": "Taleo",
    "myworkdayjobs.com": "Workday",
    "workday.com": "Workday",
    "pageuppeople.com": "PageUp",
    "pageup.com": "PageUp",
    "successfactors.com": "SuccessFactors",
    "icims.com": "iCIMS",
    "cornerstoneondemand.com": "Cornerstone OnDemand",
    "csod.com": "Cornerstone OnDemand",
    "oraclecloud.com": "Oracle Recruiting Cloud",
    "peopleadmin.com": "PeopleAdmin",
    "njoyn.com": "Njoyn",
    "snaphire.com": "Snaphire",
    "greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
    "bamboohr.com": "BambooHR",
    "jobvite.com": "Jobvite",
    "breezy.hr": "Breezy",
    "recruitee.com": "Recruitee",
    "workable.com": "Workable",
    "ashbyhq.com": "Ashby",
    "ultipro.com": "UKG/Ultipro",
    "ukg.com": "UKG",
    "t1cloud.com": "T1Cloud/CiAnywhere",
    "avature.net": "Avature",
    "jobs2web.com": "Jobs2Web",
    "hrsmart.com": "HRSmart",
    "applytojob.com": "JazzHR",
}

STRONG = [
    r"faculty[\s\-_]?(position|opening|vacanc|job|career)",
    r"academic[\s\-_]?(position|opening|vacanc|job|career)",
]
MEDIUM = [
    r"\bcareers?\b", r"\bjobs?\b", r"\bvacanc",
    r"work[\s\-_]?with[\s\-_]?us", r"work[\s\-_]?for[\s\-_]?us",
    r"work[\s\-_]?at\b", r"join[\s\-_]?us", r"join[\s\-_]?our[\s\-_]?team",
    r"staff[\s\-_]?vacanc", r"employment", r"current[\s\-_]?vacanc",
    r"open[\s\-_]?position", r"we[\s\-_']?re[\s\-_]?hiring",
]
WEAK = [
    r"human[\s\-_]?resources", r"\bhr\b", r"recruit", r"\bopportunities\b",
]
NEGATIVE = [
    r"career[\s\-_]?(advi|service|centre|center|develop|coach|counsel|resource|fair|day|readiness)",
    r"\bstudents?\b", r"\badmission", r"apply[\s\-_]?now", r"scholarship",
    r"\bnews\b", r"\bevents?\b", r"donat", r"alumni", r"\blogin\b", r"privacy",
    r"cookie", r"sitemap", r"\.pdf$", r"internship", r"finding[\s\-_]?a[\s\-_]?job",
]

STRONG_RE = [re.compile(p, re.I) for p in STRONG]
MEDIUM_RE = [re.compile(p, re.I) for p in MEDIUM]
WEAK_RE = [re.compile(p, re.I) for p in WEAK]
NEG_RE = [re.compile(p, re.I) for p in NEGATIVE]


def ats_domain_for(url):
    host = urlparse(url).netloc.lower()
    for domain, label in ATS_DOMAINS.items():
        if domain in host:
            return label
    return None


def score_link(href, text):
    hay = ((href or "") + " " + (text or "")).lower()
    for p in NEG_RE:
        if p.search(hay):
            return -1
    score = 0
    for p in STRONG_RE:
        if p.search(hay):
            score += 5
    for p in MEDIUM_RE:
        if p.search(hay):
            score += 2
    for p in WEAK_RE:
        if p.search(hay):
            score += 1
    return score


def best_link_from_anchors(anchors, final_url):
    best_url, best_score, best_ats = None, 0, None
    seen = set()
    for href, text in anchors:
        href = (href or "").strip()
        if not href or href.startswith("#") or href.lower().startswith(("mailto:", "tel:", "javascript:")):
            continue
        abs_url = urljoin(final_url, href)
        if not abs_url.startswith("http") or abs_url in seen:
            continue
        seen.add(abs_url)

        ats = ats_domain_for(abs_url)
        s = score_link(href, text)
        if ats and s >= 0:
            # Known ATS domain is a strong signal on its own even if the
            # anchor text/href itself didn't match our keyword patterns.
            s += 6
        if s <= 0:
            continue
        if s > best_score:
            best_score, best_url, best_ats = s, abs_url, ats
    if best_url:
        return best_url, best_ats, f"OK:{best_score}"
    return None, None, "NO_MATCH"


def fetch_anchors_requests(url, timeout=12):
    resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    if resp.status_code >= 400:
        raise requests.HTTPError(f"HTTP_{resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = [(a.get("href"), a.get_text(" ", strip=True)) for a in soup.find_all("a", href=True)]
    return anchors, resp.url


def find_link_requests(base_url):
    """Homepage fetch + one extra hop if the best candidate isn't already a
    known ATS domain (schools often link to a 'Careers' hub page that itself
    links onward to the real ATS portal)."""
    anchors, final_url = fetch_anchors_requests(base_url)
    link, ats, status = best_link_from_anchors(anchors, final_url)
    if link and not ats:
        try:
            hop_anchors, hop_final = fetch_anchors_requests(link)
            hop_link, hop_ats, hop_status = best_link_from_anchors(hop_anchors, hop_final)
            if hop_link and hop_ats:
                return hop_link, hop_ats, f"OK-2hop:{hop_status}"
        except Exception:
            pass
    return link, ats, status


def process_row_requests(row):
    url = row["base_url"].strip()
    if not url:
        row["status_internal"] = "NO_BASE_URL"
        return row
    try:
        link, ats, status = find_link_requests(url)
        row["careers_link"] = link or ""
        row["ats_platform"] = ats or ""
        row["confidence"] = "high" if ats else ("medium" if link else "not_found")
        row["notes"] = status
        row["status_internal"] = "DONE" if link else "RETRY_PLAYWRIGHT"
    except Exception as e:
        row["status_internal"] = "RETRY_PLAYWRIGHT"
        row["notes"] = f"requests_failed:{type(e).__name__}"
    return row


def process_row_playwright(context, row):
    url = row["base_url"].strip()
    page = context.new_page()
    try:
        page.goto(url, timeout=20000, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        anchors = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => [e.getAttribute('href'), e.innerText || ''])"
        )
        final_url = page.url
        link, ats, status = best_link_from_anchors(anchors, final_url)
        if link and not ats:
            try:
                page2 = context.new_page()
                page2.goto(link, timeout=20000, wait_until="domcontentloaded")
                page2.wait_for_timeout(1000)
                hop_anchors = page2.eval_on_selector_all(
                    "a[href]", "els => els.map(e => [e.getAttribute('href'), e.innerText || ''])"
                )
                hop_link, hop_ats, hop_status = best_link_from_anchors(hop_anchors, page2.url)
                page2.close()
                if hop_link and hop_ats:
                    link, ats, status = hop_link, hop_ats, f"OK-2hop:{hop_status}"
            except Exception:
                pass
        row["careers_link"] = link or ""
        row["ats_platform"] = ats or ""
        row["confidence"] = "high" if ats else ("medium" if link else "not_found")
        row["notes"] = status + " [playwright]"
    except Exception as e:
        row["careers_link"] = ""
        row["ats_platform"] = ""
        row["confidence"] = "not_found"
        row["notes"] = f"playwright_failed:{type(e).__name__}"
    finally:
        page.close()
    return row


def save_checkpoint(all_rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                         help="only process this many remaining schools (for testing)")
    args = parser.parse_args()

    with open(CSV_PATH, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    todo_idx = [i for i, r in enumerate(all_rows) if not r.get("careers_link")]
    if args.limit:
        todo_idx = todo_idx[:args.limit]

    total = len(todo_idx)
    print(f"{len(all_rows)} schools total, {total} still need a careers link.")
    if total == 0:
        print("Nothing to do.")
        return

    from playwright.sync_api import sync_playwright

    t0 = time.time()
    processed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(user_agent=UA, viewport={"width": 1366, "height": 900})

        for chunk_start in range(0, total, CHUNK_SIZE):
            chunk_idx = todo_idx[chunk_start:chunk_start + CHUNK_SIZE]

            # Fast pass: plain requests, concurrent.
            with ThreadPoolExecutor(max_workers=REQUESTS_WORKERS) as ex:
                futures = {ex.submit(process_row_requests, all_rows[i]): i for i in chunk_idx}
                for fut in as_completed(futures):
                    i = futures[fut]
                    all_rows[i] = fut.result()

            # Fallback pass: real browser, for anything requests couldn't get through.
            retry_idx = [i for i in chunk_idx if all_rows[i].get("status_internal") == "RETRY_PLAYWRIGHT"]
            for i in retry_idx:
                all_rows[i] = process_row_playwright(context, all_rows[i])

            for i in chunk_idx:
                all_rows[i].pop("status_internal", None)

            processed += len(chunk_idx)
            elapsed = time.time() - t0
            print(f"  {processed}/{total} processed ({elapsed:.0f}s elapsed) -- saving checkpoint...", flush=True)
            save_checkpoint(all_rows)

        browser.close()

    ok = sum(1 for r in all_rows if r.get("careers_link"))
    print(f"\nDone in {time.time()-t0:.0f}s. {ok}/{len(all_rows)} schools now have a careers link.")
    print(f"Saved to {CSV_PATH}")


if __name__ == "__main__":
    main()
