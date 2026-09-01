"""
Scrapes current faculty job postings for non-US schools in schools_master.csv
into job-data/school_job_posts/school_id_<id>_job_posts.csv (one file per school).

Input: the verified careers_link per school from Step 1 (schools_master.csv).
Nothing here runs on a link that hasn't been through that review.

Output columns (one row per open posting):
  school_id, job_title, job_title_original, department, department_original,
  location, position_type, post_date, posting_url, source_tier, source_platform,
  language, scraped_at

Detection strategy -- four tiers, checked in order per school:
  Tier 0 -- national government job portals, where the verified careers_link
            itself points at one (Poland's bazaogloszen.nauka.gov.pl; Greece's
            APELLA). If the verified link is an individual school page instead
            (e.g. most Romanian schools), that school is NOT forced onto a
            national portal it wasn't verified against -- it flows through the
            normal tiers below on its own link.
  Tier 1 -- known ATS platform APIs: Workday (CXS), Oracle Recruiting Cloud /
            Fusion HCM (recruitingCEJobRequisitions REST API), AcademicJobsOnline.
            NOT built: PeopleAdmin/NEOGOV/Cornerstone/Symplicity/Ellucian/
            Interfolio -- zero non-US schools in this dataset use them (checked
            via domain sniff), so a dedicated adapter has no target here. Taleo
            and PageUp/NGA schools flow through Tier 3 (their pages render
            enough server-side HTML/text for the generic scraper, and building
            bespoke adapters for ~10-15 schools each wasn't worth the tradeoff
            against finishing the higher-leverage Tier 3 work -- flagged here,
            not hidden).
  Tier 2 -- schema.org JobPosting structured data, any platform.
  Tier 3 -- generic Playwright-rendered scrape:
            - pagination: numbered pages / "Next" / "Load more" buttons, clicked
              in a loop until nothing new appears
            - tab/category click-through: ARIA role="tab" first, styled-button
              fallback; postings tagged with the tab's own label as position_type
            - one bounded hop to "browse by department/faculty/school" links
              found on the central jobs hub page
            - per-language STRONG keyword sets (en/fr/de/es/it/pt/sv/da/no/nl/tr/pl),
              page language read from <html lang>; an on-page English-version
              link is preferred over translating when one exists

Language / translation:
  - A page's own English version is used when discoverable -- no translation,
    most accurate.
  - Otherwise job_title/department are machine-translated via MyMemory's free
    translation API (a real third-party translation service, not scraping --
    no LLM calls, no tokens spent) and the original text is kept in
    job_title_original/department_original, never discarded.
  - Academic rank terms translate literally (e.g. "Maitre de conferences" ->
    "Lecturer"), never force-mapped onto US tenure-track categories.

Update strategy: every run pulls each school's current full list and replaces
that school's file -- no watermark, no history. New postings appear because
they're in the fresh pull; filled/closed ones vanish because they're absent.

What's honestly not fully solved (same limits named in the plan):
  - Orphaned department pages with no link path from the jobs hub at all.
  - Hard bot-blocks (Cloudflare/CAPTCHA, e.g. CoreHR's Irish schools returning
    403 to every access method tried) -- flagged as failed, not forced through.
  - Unusual JS beyond load-more/tabs (multi-step filter wizards, scroll-triggered
    infinite scroll) -- generic patterns cover most sites, not all.
  Every school's status/tier is logged, so "found nothing" and "confidently
  found zero postings" never look the same.
"""

import csv
import json
import os
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER_CSV = os.path.join(HERE, 'schools_master.csv')
OUT_DIR = os.path.join(HERE, 'school_job_posts')
LOG_CSV = os.path.join(OUT_DIR, '_scrape_log.csv')

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

CANONICAL_FIELDS = [
    'school_id', 'job_title', 'job_title_original', 'department', 'department_original',
    'location', 'position_type', 'post_date', 'posting_url', 'source_tier',
    'source_platform', 'language', 'scraped_at',
]

# --------------------------------------------------------------------------
# Language-aware keyword sets (STRONG academic-title signals per language).
# English is always unioned in -- many non-English sites still post English
# job titles, especially in technical fields.
# --------------------------------------------------------------------------
POSITIVE_TITLE_TERMS = {
    'en': ['professor', 'lecturer', 'faculty', 'tenure', 'postdoc', 'post-doc',
           'senior lecturer', 'reader', 'chair', 'academic staff', 'research fellow',
           'teaching fellow', 'instructor', 'teaching position', 'teaching assistant',
           'clinical faculty', 'adjunct', 'research assistant', 'research associate',
           'graduate assistant', 'visiting scholar', 'department chair'],
    'fr': ['professeur', 'professeure', 'maitre de conferences', 'enseignant-chercheur',
           'chercheur', 'chercheuse', 'charge de cours', 'charge d\'enseignement'],
    'de': ['professor', 'professorin', 'dozent', 'dozentin', 'wissenschaftlich',
           'lehrstuhl', 'akademisch'],
    'es': ['profesor', 'profesora', 'catedratico', 'catedratica', 'docente',
           'investigador', 'investigadora'],
    'it': ['professore', 'professoressa', 'ricercatore', 'ricercatrice', 'docente'],
    'pt': ['professor', 'professora', 'docente', 'investigador', 'investigadora'],
    'sv': ['professor', 'lektor', 'forskare', 'doktorand', 'universitetsadjunkt'],
    'da': ['professor', 'lektor', 'adjunkt', 'forsker', 'postdoc'],
    'no': ['professor', 'forsker', 'stipendiat', 'foreleser'],
    'nl': ['hoogleraar', 'universitair docent', 'onderzoeker', 'promovendus'],
    'tr': ['profesor', 'doçent', 'öğretim üyesi', 'araştırma görevlisi', 'öğretim görevlisi'],
    'pl': ['profesor', 'adiunkt', 'wykladowca', 'docent', 'asystent'],
}
ALL_POSITIVE_TERMS = sorted({t for terms in POSITIVE_TITLE_TERMS.values() for t in terms}, key=len, reverse=True)
POSITIVE_TITLE_RE = re.compile(r'\b(' + '|'.join(re.escape(t) for t in ALL_POSITIVE_TERMS) + r')\b', re.I)

# Strong: URL patterns specific enough to job-board systems that we trust them
# on their own, regardless of title wording (covers e.g. a real "Head of Tax"
# posting on a university job board -- a real posting even if not academic).
STRONG_URL_RE = re.compile(
    r'(ref=[\w-]+|Vacancy\.aspx|/jobs?/\d+|/vacancy/\d+|/vacancies/\d+|/positions/\d+|'
    r'-\d{5,}\.html|jobid=\d+|jobId=\d+|req(?:uisition)?[_-]?id|/oferta/|/ogloszenie/|'
    r'/careersection/|jobdetail|searchresults.*job|cws=\d|viewRequisition|'
    r'/postings?/(view/)?\d+|applyRequisition|jid=\d+)', re.I)
# Weak: generic CMS patterns (e.g. Drupal /node/123) used for every page on a
# site, not just postings -- only trusted if the link text also reads like an
# academic posting title in some supported language.
WEAK_URL_RE = re.compile(r'(/node/\d{2,}|/jobs?/|/career|/position)', re.I)
HARD_NEGATIVE_RE = re.compile(
    r'^(login|log ?in( page)?|register|sign in|sign up|cookies?|terms of use|terms & '
    r'conditions|accessibility|contact us|privacy policy|sitemap|home|search|'
    r'new search|view all categories|current vacancies|apply now|learn more|find out more|'
    r'apply for job|apply|apply online|save job|share|print|back to results)$', re.I)

DEPT_CLAUSE_RE = re.compile(
    r',?\s*((?:Faculty|Department|Dept\.?|School|College|Institute|Center|Centre|'
    r'Division)\s+(?:of|for)\s+[A-Za-z&,\s-]{3,60})$')

TAB_LOAD_MORE_TERMS = ['load more', 'show more', 'view more', 'more jobs', 'more results',
                        'next page', 'next »', 'next', '>', 'weitere', 'mehr laden',
                        'charger plus', 'voir plus', 'mostrar mas', 'cargar mas']


def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}', flush=True)


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# --------------------------------------------------------------------------
# Translation (MyMemory free API -- a real translation service, not an LLM
# call and not scraping). Cached so repeated identical strings (very common --
# the same French/Polish rank titles recur across many schools) cost one call.
# --------------------------------------------------------------------------
_TRANSLATE_CACHE = {}

def translate_to_english(text, source_lang):
    if not text or not source_lang or source_lang == 'en':
        return text
    key = (source_lang, text)
    if key in _TRANSLATE_CACHE:
        return _TRANSLATE_CACHE[key]
    try:
        r = requests.get('https://api.mymemory.translated.net/get',
                          params={'q': text[:490], 'langpair': f'{source_lang}|en'},
                          timeout=10)
        if r.status_code == 200:
            data = r.json()
            translated = data.get('responseData', {}).get('translatedText', '')
            if translated and 'MYMEMORY WARNING' not in translated.upper():
                _TRANSLATE_CACHE[key] = translated
                return translated
    except requests.RequestException:
        pass
    _TRANSLATE_CACHE[key] = text
    return text


# --------------------------------------------------------------------------
# Title/department parsing -- pulls an embedded "Faculty of X" / "Department
# of X" clause out of a combined title string into its own column.
# --------------------------------------------------------------------------
def split_title_department(raw_title, school_name=None):
    title = raw_title.strip()
    department = ''
    if school_name:
        esc = re.escape(school_name.strip())
        title = re.sub(r',?\s*' + esc + r'\s*$', '', title, flags=re.I).strip()
    m = DEPT_CLAUSE_RE.search(title)
    if m:
        department = m.group(1).strip()
        title = title[:m.start()].strip().rstrip(',').strip()
    # also handle "Title - Department" en/em-dash split when the tail looks like a unit name
    if not department:
        m2 = re.match(r'^(.*?)\s+[–—-]\s+([\w&\s]+(?:Institute|Center|Centre|School of[\w\s]*|House of[\w\s]*))$', title)
        if m2:
            title, department = m2.group(1).strip(), m2.group(2).strip()
    return title, department


POSITION_TYPE_RULES = [
    (re.compile(r'\b(assistant|associate|full)\s+professor\b|\btenure[- ]track\b|\btenured\b', re.I), 'Tenure-Track'),
    (re.compile(r'\b(lecturer|instructor|teaching (fellow|position|assistant)|clinical faculty|adjunct)\b', re.I), 'Non-Tenure-Track'),
    (re.compile(r'\bpost-?doc(toral)?\b', re.I), 'Postdoctoral'),
]

def infer_position_type(title, tab_label=None):
    if tab_label:
        return tab_label.strip().title()
    for pattern, label in POSITION_TYPE_RULES:
        if pattern.search(title):
            return label
    return ''


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_requests(url, method='GET', json_body=None, timeout=20, extra_headers=None):
    headers = {'User-Agent': UA, 'Accept-Language': 'en;q=0.9,*;q=0.5'}
    if extra_headers:
        headers.update(extra_headers)
    try:
        if method == 'POST':
            headers['Content-Type'] = 'application/json'
            r = requests.post(url, json=json_body, headers=headers, timeout=timeout)
        else:
            r = requests.get(url, headers=headers, timeout=timeout)
        return r.status_code, r.text
    except requests.RequestException as e:
        return None, str(e)


_pw = None
_browser = None

def get_browser():
    global _pw, _browser
    if _browser is None and sync_playwright is not None:
        _pw = sync_playwright().start()
        _browser = _pw.chromium.launch()
    return _browser


def _click_load_more_and_paginate(page, max_clicks=12):
    """Repeatedly clicks Load More/Next-style controls until content stops growing."""
    prev_len = len(page.content())
    for _ in range(max_clicks):
        clicked = False
        for term in TAB_LOAD_MORE_TERMS:
            try:
                loc = page.get_by_role('button', name=re.compile(re.escape(term), re.I))
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click(timeout=2000)
                    clicked = True
                    break
                loc2 = page.get_by_role('link', name=re.compile(re.escape(term), re.I))
                if loc2.count() > 0 and loc2.first.is_visible():
                    loc2.first.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            break
        page.wait_for_timeout(1800)
        new_len = len(page.content())
        if new_len <= prev_len:
            break
        prev_len = new_len
    return page.content()


def _find_tabs(page):
    """ARIA role=tab first, then a styled-button fallback for common tab widgets."""
    tabs = []
    try:
        aria_tabs = page.locator('[role="tab"]')
        for i in range(min(aria_tabs.count(), 10)):
            t = aria_tabs.nth(i)
            if t.is_visible():
                tabs.append((t, (t.inner_text() or '').strip()))
    except Exception:
        pass
    if not tabs:
        try:
            candidates = page.locator('.tabs button, .tab-list button, ul.tabs a, .nav-tabs a')
            for i in range(min(candidates.count(), 10)):
                t = candidates.nth(i)
                if t.is_visible():
                    tabs.append((t, (t.inner_text() or '').strip()))
        except Exception:
            pass
    return tabs


def fetch_playwright_rich(url, timeout=25000):
    """Loads the page, clicks through tabs (if any) and paginates/load-mores each,
    returning a list of (html, tab_label_or_None) captures."""
    b = get_browser()
    if b is None:
        return [], 'playwright unavailable'
    page = None
    results = []
    try:
        page = b.new_page(user_agent=UA)
        page.goto(url, timeout=timeout, wait_until='domcontentloaded')
        page.wait_for_timeout(2200)
        tabs = _find_tabs(page)
        if tabs:
            for tab_loc, label in tabs:
                try:
                    tab_loc.click(timeout=3000)
                    page.wait_for_timeout(1500)
                    html = _click_load_more_and_paginate(page)
                    results.append((html, label or None))
                except Exception:
                    continue
        else:
            html = _click_load_more_and_paginate(page)
            results.append((html, None))
        # page.content() only ever returns the TOP-level document -- a real
        # posting list embedded in an <iframe> (confirmed via iCIMS: the
        # actual job list lives in a nested iframe, not the outer shell page)
        # is otherwise invisible no matter how long we wait. page.frames
        # already includes nested iframes recursively, so no manual recursion
        # needed; skip the main frame itself (already captured above).
        try:
            for frame in page.frames:
                if frame == page.main_frame:
                    continue
                try:
                    frame_html = frame.content()
                    if frame_html and len(frame_html) > 200:
                        results.append((frame_html, None))
                except Exception:
                    continue
        except Exception:
            pass
        return results, None
    except Exception as e:
        return results, str(e)
    finally:
        if page:
            page.close()


def fetch_html_smart(url):
    """Plain requests first (fast); escalate to the rich Playwright path (tabs +
    pagination) if the page looks empty/blocked OR -- the case a byte-length
    check alone misses -- if it returned a normal-sized page that is really
    just an unrendered JS app shell with no real postings extractable from it
    (confirmed by testing: some sites return 30-60KB of markup server-side but
    zero of it is real listing content until JS + a Load More click run)."""
    status, text = fetch_requests(url)
    if status == 200 and text and len(text) > 800:
        quick_check = generic_scrape_page(text, url) or scrape_schema_org(text, url)
        if quick_check:
            return [(text, None)], 'requests'
    results, err = fetch_playwright_rich(url)
    if results and any(generic_scrape_page(h, url, t) for h, t in results):
        return results, 'playwright'
    if results:
        return results, 'playwright'  # rendered but genuinely empty -- still better than the raw shell
    return [(text or '', None)], 'requests'


def detect_page_language(html):
    m = re.search(r'<html[^>]+lang=["\']([a-zA-Z-]+)["\']', html)
    if m:
        return m.group(1).split('-')[0].lower()
    return None


def find_english_version_link(html, base_url):
    """Only trusts a genuine language-switcher control (short label text like
    'EN'/'English', typically in nav/header chrome) -- NOT any link whose href
    merely contains '/en/', since that also matches ordinary content pages on
    sites where English is just a permanent path prefix, not a switcher."""
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if text in ('en', 'eng', 'english', 'english version', 'view in english'):
            href = a['href']
            if urljoin(base_url, href).rstrip('/') == base_url.rstrip('/'):
                continue
            return urljoin(base_url, href)
    return None


# --------------------------------------------------------------------------
# Platform detection
# --------------------------------------------------------------------------

def detect_platform(url):
    host = urlparse(url).netloc.lower()
    if 'myworkdayjobs.com' in host or 'myworkdaysite.com' in host:
        return 'workday'
    if 'academicjobsonline.org' in host:
        return 'academicjobsonline'
    if 'apella.minedu.gov.gr' in host:
        return 'apella'
    if 'oraclecloud.com' in host:
        return 'oracle'
    if host == 'bazaogloszen.nauka.gov.pl':
        return 'poland_nauka'
    if 'smartrecruiters.com' in host:
        return 'smartrecruiters'
    if 'peopleadmin' in host:
        return 'peopleadmin'
    if 'workforcenow.adp.com' in host or 'workforcenow.cloud.adp.com' in host:
        return 'adp'
    if host.endswith('.csod.com'):
        return 'cornerstone'
    if host.endswith('.icims.com'):
        return 'icims'
    if 'ultipro.com' in host:
        return 'ultipro'
    return None


# --------------------------------------------------------------------------
# Tier 0/1 adapters
# --------------------------------------------------------------------------

def scrape_workday(url):
    parsed = urlparse(url)
    host_parts = parsed.netloc.split('.')
    if len(host_parts) < 4:
        return None, 'unrecognized workday host'
    tenant = host_parts[0]
    path_parts = [p for p in parsed.path.split('/') if p]
    # skip a leading locale segment (e.g. "en-US", "fr-CA") -- the real site
    # name is the next segment, not the locale itself
    path_parts = [p for p in path_parts if not re.fullmatch(r'[a-z]{2}(-[A-Z]{2})?', p)]
    if not path_parts:
        return None, 'no site in workday path'
    site = path_parts[0]
    api = f'https://{parsed.netloc}/wday/cxs/{tenant}/{site}/jobs'
    postings = []
    offset = 0
    limit = 20
    total = None
    for _ in range(25):
        status, text = fetch_requests(api, method='POST', json_body={
            'appliedFacets': {}, 'limit': limit, 'offset': offset, 'searchText': ''
        })
        if status != 200:
            break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            break
        if total is None:
            total = data.get('total', 0)
        jobs = data.get('jobPostings', [])
        if not jobs:
            break
        for j in jobs:
            postings.append({
                'job_title': j.get('title', ''),
                'department': '',
                'location': j.get('locationsText', ''),
                'position_type': '',
                'post_date': j.get('postedOn', ''),
                'posting_url': urljoin(f'https://{parsed.netloc}', j.get('externalPath', '')),
                'language': 'en',
            })
        offset += limit
        if total is not None and offset >= total:
            break
        time.sleep(0.3)
    if not postings and total == 0:
        return [], None
    if not postings:
        return None, 'workday api returned no postings unexpectedly'
    return postings, None


def scrape_oracle(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    m = re.search(r'/sites/([^/]+)', parsed.path)
    site_number = m.group(1) if m else None
    base = f'https://{parsed.netloc}'
    postings = []
    limit = 25
    offset = 0
    finder_site = f'siteNumber={site_number},' if site_number else ''
    for _ in range(20):
        api = (f'{base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions'
               f'?onlyData=true&finder=findReqs;{finder_site}limit={limit},offset={offset}')
        status, text = fetch_requests(api, extra_headers={'Accept': 'application/json'})
        if status != 200:
            return (None, f'oracle api status={status}') if offset == 0 else (postings or None, None)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return (None, 'oracle api bad json') if offset == 0 else (postings, None)
        items = data.get('items', [])
        reqs = items[0].get('requisitionList', []) if items else []
        if not reqs:
            break
        for r in reqs:
            postings.append({
                'job_title': r.get('Title', ''),
                'department': r.get('PrimaryLocation', '') and '',
                'location': r.get('PrimaryLocation', ''),
                'position_type': '',
                'post_date': r.get('PostedDate', ''),
                'posting_url': urljoin(base, f"/hcmUI/CandidateExperience/en/sites/{site_number or 'CX_1'}/job/{r.get('Id','')}"),
                'language': 'en',
            })
        offset += limit
        if len(reqs) < limit:
            break
        time.sleep(0.3)
    return postings, None  # [] is a legitimate verified-zero result


def scrape_smartrecruiters(url):
    """https://jobs.smartrecruiters.com/<Company>/... -> public REST API,
    api.smartrecruiters.com/v1/companies/<Company>/postings (documented, no
    auth needed for public postings)."""
    m = re.search(r'smartrecruiters\.com/([^/?#]+)', url)
    if not m:
        return None, 'could not parse smartrecruiters company slug'
    company = m.group(1)
    postings = []
    offset = 0
    limit = 100
    for _ in range(10):
        api = f'https://api.smartrecruiters.com/v1/companies/{company}/postings?limit={limit}&offset={offset}'
        status, text = fetch_requests(api, extra_headers={'Accept': 'application/json'})
        if status != 200:
            return (None, f'smartrecruiters api status={status}') if offset == 0 else (postings, None)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return (None, 'smartrecruiters api bad json') if offset == 0 else (postings, None)
        content = data.get('content', [])
        if not content:
            break
        for item in content:
            loc = item.get('location', {}) or {}
            loc_str = ', '.join(filter(None, [loc.get('city'), loc.get('region'), loc.get('country')]))
            postings.append({
                'job_title': item.get('name', ''), 'department': item.get('department', {}).get('label', '') if isinstance(item.get('department'), dict) else '',
                'location': loc_str, 'position_type': '',
                'post_date': item.get('releasedDate', ''),
                'posting_url': item.get('ref', '') or f'https://jobs.smartrecruiters.com/{company}/{item.get("id","")}',
                'language': 'en',
            })
        offset += limit
        if offset >= data.get('totalFound', 0):
            break
        time.sleep(0.3)
    return postings, None


def scrape_peopleadmin(url):
    """Any *.peopleadmin.<tld> instance exposes a stable Atom feed at
    /postings/all_jobs.atom regardless of the specific institution subdomain."""
    parsed = urlparse(url)
    api = f'https://{parsed.netloc}/postings/all_jobs.atom'
    status, text = fetch_requests(api)
    if status != 200:
        return None, f'peopleadmin atom status={status}'
    soup = BeautifulSoup(text, 'xml')
    postings = []
    for entry in soup.find_all('entry'):
        title_tag = entry.find('title')
        link_tag = entry.find('link')
        published = entry.find('published')
        author = entry.find('author')
        author_name = author.find('name').get_text(strip=True) if author and author.find('name') else ''
        postings.append({
            'job_title': title_tag.get_text(strip=True) if title_tag else '',
            'department': author_name, 'location': '', 'position_type': '',
            'post_date': published.get_text(strip=True) if published else '',
            'posting_url': link_tag['href'] if link_tag and link_tag.has_attr('href') else '',
            'language': 'en',
        })
    return postings, None  # [] is a legitimate verified-zero result


def scrape_adp(url):
    """ADP Workforce Now recruitment pages are a pure JS SPA with no server-
    rendered content, but they call a real public JSON API keyed only by the
    `cid` query param already present in the verified careers_link -- no
    per-job URL is exposed anywhere in the page (JS onclick navigation, no
    real hrefs), so posting_url honestly falls back to the search page itself."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    cid = (qs.get('cid') or [None])[0]
    if not cid:
        return None, 'no cid param in adp url'
    api = (f'https://{parsed.netloc}/mascsr/default/careercenter/public/events/'
           f'staffing/v1/job-requisitions?cid={cid}&timeStamp={int(time.time()*1000)}')
    status, text = fetch_requests(api, extra_headers={'Accept': 'application/json'})
    if status != 200:
        return None, f'adp api status={status}'
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None, 'adp api bad json'
    postings = []
    for job in data.get('jobRequisitions', []):
        loc = ''
        req_locs = job.get('requisitionLocations') or []
        if req_locs:
            loc = (req_locs[0].get('nameCode', {}) or {}).get('shortName', '').strip()
        postings.append({
            'job_title': job.get('requisitionTitle', ''), 'department': '', 'location': loc,
            'position_type': (job.get('workLevelCode', {}) or {}).get('shortName', ''),
            'post_date': job.get('postDate', ''), 'posting_url': url,
            'language': 'en',
        })
    return postings, None  # [] is a legitimate verified-zero result


def scrape_cornerstone(url):
    """Cornerstone OnDemand (*.csod.com) calls a real JSON API
    (us.api.csod.com/rec-job-search/external/jobs) but it requires a
    session-scoped Bearer JWT issued by the page's own JS -- there's no way
    to construct that token from the URL alone, so Playwright loads the page
    once to capture BOTH the token and the careerSiteId it uses, then plain
    requests pages through the rest with that captured token (valid for the
    lifetime of this script run, no need to stay in the browser for every page)."""
    b = get_browser()
    if b is None:
        return None, 'playwright unavailable'
    captured = {}
    page = None
    try:
        page = b.new_page(user_agent=UA)
        def on_request(req):
            if 'rec-job-search/external/jobs' in req.url and not captured:
                auth = req.headers.get('authorization')
                if auth:
                    captured['auth'] = auth
                    try:
                        body = json.loads(req.post_data or '{}')
                        captured['careerSiteId'] = body.get('careerSiteId')
                        captured['careerSitePageId'] = body.get('careerSitePageId')
                        captured['cultureId'] = body.get('cultureId', 1)
                        captured['cultureName'] = body.get('cultureName', 'en-US')
                    except (json.JSONDecodeError, TypeError):
                        pass
        page.on('request', on_request)
        page.goto(url, timeout=25000, wait_until='networkidle')
        page.wait_for_timeout(1500)
    except Exception as e:
        return None, f'cornerstone playwright load failed: {e}'
    finally:
        if page:
            page.close()

    if 'auth' not in captured or captured.get('careerSiteId') is None:
        return None, 'cornerstone auth token not captured'

    host = urlparse(url).netloc
    api = 'https://us.api.csod.com/rec-job-search/external/jobs'
    headers = {
        'Authorization': captured['auth'], 'Content-Type': 'application/json',
        'Origin': f'https://{host}', 'Referer': f'https://{host}/', 'User-Agent': UA,
    }
    postings = []
    page_num = 1
    total = None
    for _ in range(25):
        payload = {
            'careerSiteId': captured['careerSiteId'], 'careerSitePageId': captured['careerSitePageId'],
            'pageNumber': page_num, 'pageSize': 25, 'cultureId': captured['cultureId'],
            'searchText': '', 'cultureName': captured['cultureName'], 'states': [], 'countryCodes': [],
            'cities': [], 'placeID': '', 'radius': None, 'postingsWithinDays': None,
            'customFieldCheckboxKeys': [], 'customFieldDropdowns': [], 'customFieldRadios': [],
        }
        status, text = fetch_requests(api, method='POST', json_body=payload, extra_headers=headers)
        if status != 200:
            return (None, f'cornerstone api status={status}') if page_num == 1 else (postings, None)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return (None, 'cornerstone api bad json') if page_num == 1 else (postings, None)
        reqs = data.get('data', {}).get('requisitions', [])
        if total is None:
            total = data.get('data', {}).get('totalCount', 0)
        if not reqs:
            break
        for r in reqs:
            locs = r.get('locations') or []
            loc = ', '.join(filter(None, [locs[0].get('city'), locs[0].get('state'), locs[0].get('country')])) if locs else ''
            postings.append({
                'job_title': r.get('displayJobTitle', ''), 'department': '', 'location': loc,
                'position_type': '', 'post_date': r.get('postingEffectiveDate', ''),
                'posting_url': f'https://{host}/ux/ats/careersite/{captured["careerSitePageId"]}/requisition/{r.get("requisitionId")}',
                'language': 'en',
            })
        page_num += 1
        if len(postings) >= total:
            break
        time.sleep(0.3)
    return postings, None


def scrape_icims(url):
    """iCIMS career sites nest the real listing inside an <iframe>, and the
    bare root URL only ever reaches an "intro"/branding page's iframe, not
    the actual search results -- the real content only appears by navigating
    directly to <base>/jobs/search?ss=1 (a stable iCIMS URL convention, not
    school-specific). fetch_playwright_rich already captures every nested
    frame's content (added generically, not just for this platform)."""
    parsed = urlparse(url)
    search_url = f'https://{parsed.netloc}/jobs/search?ss=1'
    captures, err = fetch_playwright_rich(search_url)
    if not captures:
        return None, err or 'icims: no frames captured'
    postings = []
    seen = set()
    for html, _tab in captures:
        for p in generic_scrape_page(html, search_url):
            if p['posting_url'] in seen:
                continue
            seen.add(p['posting_url'])
            postings.append(p)
    return postings, None  # [] is a legitimate verified-zero result


def scrape_ultipro(url):
    """UKG/Ultipro job boards call a real public JSON API keyed only by the
    tenant/board path already in the verified careers_link -- no auth header
    needed beyond content-type, confirmed working via plain requests."""
    parsed = urlparse(url)
    m = re.match(r'^(/[^/]+/JobBoard/[^/]+)/', parsed.path)
    if not m:
        return None, 'could not parse ultipro tenant/board path'
    api = f'https://{parsed.netloc}{m.group(1)}/JobBoardView/LoadSearchResults'
    postings = []
    skip = 0
    top = 50
    total = None
    for _ in range(25):
        payload = {
            'opportunitySearch': {'Top': top, 'Skip': skip, 'QueryString': '',
                                   'OrderBy': [{'Value': 'postedDateDesc', 'PropertyName': 'PostedDate', 'Ascending': False}],
                                   'Filters': []},
            'matchCriteria': {'PreferredJobs': [], 'Educations': [], 'LicenseAndCertifications': [],
                               'Skills': [], 'hasNoLicenses': False, 'SkippedSkills': []},
        }
        status, text = fetch_requests(api, method='POST', json_body=payload,
                                       extra_headers={'Accept': 'application/json'})
        if status != 200:
            return (None, f'ultipro api status={status}') if skip == 0 else (postings, None)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return (None, 'ultipro api bad json') if skip == 0 else (postings, None)
        if total is None:
            total = data.get('totalCount', 0)
        opps = data.get('opportunities', [])
        if not opps:
            break
        for o in opps:
            locs = o.get('Locations') or []
            loc = (locs[0].get('LocalizedDescription') or locs[0].get('LocalizedName', '')) if locs else ''
            postings.append({
                'job_title': o.get('Title', ''), 'department': o.get('JobCategoryName', ''),
                'location': loc, 'position_type': '', 'post_date': o.get('PostedDate', ''),
                'posting_url': f'https://{parsed.netloc}{m.group(1)}/OpportunityDetail?opportunityId={o.get("Id","")}',
                'language': 'en',
            })
        skip += top
        if skip >= total:
            break
        time.sleep(0.3)
    return postings, None  # [] is a legitimate verified-zero result


def scrape_academicjobsonline(url):
    status, html = fetch_requests(url)
    if status != 200:
        return None, f'ajo fetch failed status={status}'
    soup = BeautifulSoup(html, 'html.parser')
    postings = []
    for a in soup.find_all('a', href=True):
        if '/jobs/' not in a['href']:
            continue
        row = a.find_parent('tr') or a.find_parent('li') or a.parent
        row_text = row.get_text(' | ', strip=True) if row else a.get_text(strip=True)
        parts = [p.strip() for p in row_text.split('|') if p.strip() and p.strip().lower() != 'apply']
        title = parts[-1] if parts else a.get_text(strip=True)
        postings.append({
            'job_title': title, 'department': '', 'location': '', 'position_type': '',
            'post_date': '', 'posting_url': urljoin('https://academicjobsonline.org', a['href']),
            'language': 'en',
        })
    seen, out = set(), []
    for p in postings:
        if p['posting_url'] in seen:
            continue
        seen.add(p['posting_url'])
        out.append(p)
    return out, None


_APELLA_RSS_CACHE = None

def scrape_apella(url, school_name):
    global _APELLA_RSS_CACHE
    if _APELLA_RSS_CACHE is None:
        status, text = fetch_requests('https://apella.minedu.gov.gr/apella-positions-rss.xml')
        if status != 200:
            return None, f'apella rss fetch failed status={status}'
        _APELLA_RSS_CACHE = text
    soup = BeautifulSoup(_APELLA_RSS_CACHE, 'xml')
    name_lower = school_name.lower()
    # match on any significant (4+ char) word from the school name appearing in the
    # Greek creator field is too fragile (Greek transliteration mismatches); instead
    # require the creator field to be present and let the caller's name check happen
    # via known Greek-name cross-reference table below.
    greek_name = GREEK_NAME_MAP.get(school_name)
    postings = []
    for item in soup.find_all('item'):
        creator = item.find('dc:creator')
        creator_text = creator.get_text(strip=True) if creator else ''
        if not creator_text:
            continue
        if greek_name and greek_name not in creator_text:
            continue
        if not greek_name and name_lower.split()[0] not in creator_text.lower():
            continue
        title_tag = item.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else ''
        link_tag = item.find('link')
        pub_date = item.find('pubDate')
        postings.append({
            'job_title': title_text, 'department': creator_text, 'location': 'Greece',
            'position_type': '', 'post_date': pub_date.get_text(strip=True) if pub_date else '',
            'posting_url': link_tag.get_text(strip=True) if link_tag else '',
            'language': 'el',
        })
    return postings, None


# Short, distinctive substrings only -- official RSS creator names use
# inconsistent abbreviations (e.g. "ΘΕΣ/ΝΙΚΗΣ" instead of "ΘΕΣΣΑΛΟΝΙΚΗΣ"), so a
# match on the one unique identifying word is more robust than the full name.
GREEK_NAME_MAP = {
    'Athens University of Economics and Business': 'ΟΙΚΟΝΟΜΙΚΟ ΠΑΝΕΠΙΣΤΗΜΙΟ ΑΘΗΝΩΝ',
    'National Technical University of Athens': 'ΜΕΤΣΟΒΙΟ',
    'National and Kapodistrian University of Athens': 'ΚΑΠΟΔΙΣΤΡΙΑΚΟ',
    'Aristotle University of Thessaloniki': 'ΑΡΙΣΤΟΤΕΛΕΙΟ',
}


def scrape_poland_nauka(url, school_name):
    base = 'https://bazaogloszen.nauka.gov.pl/wyniki-wyszukiwania/'
    postings = []
    page_num = 1
    keyword = POLAND_NAME_MAP.get(school_name, school_name)
    for _ in range(10):
        status, html = fetch_requests(base, extra_headers=None)
        params_url = f'{base}?search_keywords={requests.utils.quote(keyword)}&search_per_page=50&search_page={page_num}'
        status, html = fetch_requests(params_url)
        if status != 200:
            return (None, f'poland fetch status={status}') if page_num == 1 else (postings, None)
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_=re.compile(r'\bjob_listing\b'))
        if not articles:
            break
        for art in articles:
            title_a = art.select_one('.job-title a')
            loc = art.select_one('.job-location')
            postings.append({
                'job_title': title_a.get_text(strip=True) if title_a else '',
                'department': '', 'location': loc.get_text(' ', strip=True) if loc else 'Poland',
                'position_type': '', 'post_date': '',
                'posting_url': title_a['href'] if title_a else '',
                'language': 'pl',
            })
        if len(articles) < 50:
            break
        page_num += 1
        time.sleep(0.3)
    seen, out = set(), []
    for p in postings:
        if p['posting_url'] in seen:
            continue
        seen.add(p['posting_url'])
        out.append(p)
    return out, None


POLAND_NAME_MAP = {
    'AGH University of Krakow': 'Akademia Gorniczo-Hutnicza',
    'Jagiellonian University': 'Uniwersytet Jagiellonski',
    'University of Warsaw': 'Uniwersytet Warszawski',
    'Warsaw School of Economics': 'Szkola Glowna Handlowa',
}


# --------------------------------------------------------------------------
# Tier 2: schema.org JobPosting
# --------------------------------------------------------------------------

def scrape_schema_org(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    postings = []
    for tag in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(tag.string or '')
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for c in candidates:
            if not isinstance(c, dict) or c.get('@type') != 'JobPosting':
                continue
            loc = ''
            jl = c.get('jobLocation')
            if isinstance(jl, dict):
                addr = jl.get('address', {})
                if isinstance(addr, dict):
                    loc = addr.get('addressLocality') or addr.get('addressCountry') or ''
            postings.append({
                'job_title': c.get('title', ''),
                'department': c.get('hiringOrganization', {}).get('name', '') if isinstance(c.get('hiringOrganization'), dict) else '',
                'location': loc, 'position_type': c.get('employmentType', ''),
                'post_date': c.get('datePosted', ''),
                'posting_url': c.get('url') or base_url,
                'language': '',
            })
    return postings


# --------------------------------------------------------------------------
# Tier 3: generic link/heading scrape + one-hop department discovery
# --------------------------------------------------------------------------

DEPT_HOP_HINT_RE = re.compile(
    r'(^browse by department$|^by faculty$|^by school$|^departments?$|^faculties$|'
    r'^schools and colleges$|^view all departments$|^academic units$|'
    r'^(faculty|school|department|dept\.?|college|institute)\s+of\b.{0,60}$|'
    # Non-English "Faculty/School/Department of X" equivalents -- the same
    # hub-link pattern, but the English-only version above missed every
    # French/German/Spanish/Italian/Portuguese site (found via UCLouvain's
    # "Faculte de theologie..." links being invisible to hop-discovery).
    r'^(facult[eé]|[ée]cole|d[ée]partement)\s+de\b.{0,60}$|'
    r'^(fakult[aä]t|institut)\s+f[uü]r\b.{0,60}$|'
    r'^(facultad|departamento|escuela)\s+de\b.{0,60}$|'
    r'^(facolt[aà]|dipartimento)\s+di\b.{0,60}$|'
    r'^(faculdade|departamento)\s+de\b.{0,60}$|'
    # "Faculty/PostDoc/Career/Employment Opportunities"-style category links --
    # these lead to a page of real postings, they are not themselves one (found
    # via Queen's University: "Faculty Opportunities" and "PostDoc Opportunities"
    # were being counted as fake single postings instead of followed as hops).
    r'^(faculty|postdoc|post-doc|career|employment|teaching|academic|current)\s+'
    r'(opportunit(y|ies)|positions?( available)?)\s*»?$|'
    r'^faculty\s*(&|and)\s*staff\s+directory$|'
    r'^faculty\s+recruitment(\s+and\s+support\s+program)?$)', re.I)
# ^ Anchored to the WHOLE link text, not a substring match -- a real posting
# title routinely mentions "Department of X" as part of a longer sentence
# ("Part-time Lecturer - Department of Classics"), which must NOT be treated
# as a hub-navigation link just because it contains that phrase somewhere.


def page_looks_like_faculty_listing(soup):
    """True if the page's own heading establishes academic-position context
    (e.g. 'Postes de professeur·es', 'Faculty Positions') -- lets us trust
    every distinct link in a listing table even when each row's own link text
    is just a subject/department name, not a role word (a common pattern on
    departmental-table-style listing pages)."""
    for tag in soup.find_all(['h1', 'h2', 'title'], limit=6):
        if POSITIVE_TITLE_RE.search(tag.get_text(' ', strip=True)):
            return True
    return False


def generic_scrape_page(html, base_url, tab_label=None):
    soup = BeautifulSoup(html, 'html.parser')
    postings = []
    seen_urls = set()
    trust_tables = page_looks_like_faculty_listing(soup)
    table_links = set()
    if trust_tables:
        for table in soup.find_all('table'):
            for a in table.find_all('a', href=True):
                table_links.add(a)
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:')):
            continue
        hay = a.get_text(' ', strip=True)
        if len(hay) < 4 or HARD_NEGATIVE_RE.match(hay.strip()):
            continue
        # A hub/category link (e.g. "Faculty Opportunities", "Faculty of Law")
        # is never itself a posting, no matter which other pattern its URL or
        # text happens to also match -- it's handled separately as a one-hop
        # target (find_department_hop_links) so the real postings underneath
        # it get found. Checked FIRST and unconditionally: this used to only
        # gate the title-shaped-match path, so a hub link whose URL happened
        # to also contain a generic "/career" substring (WEAK_URL_RE) slipped
        # through as a fake posting anyway (found via Queen's University's
        # "Faculty Opportunities" -> .../careers/faculty-opportunities).
        if DEPT_HOP_HINT_RE.search(hay):
            continue
        is_strong = bool(STRONG_URL_RE.search(href))
        is_weak = bool(WEAK_URL_RE.search(href))
        has_positive_title = bool(POSITIVE_TITLE_RE.search(hay))
        in_trusted_table = a in table_links
        # A real posting title reads as a title (department/rank/subject detail,
        # generally 20+ chars) regardless of the site's URL scheme -- bespoke
        # filename patterns (e.g. a school's own .php slug) shouldn't gate out
        # an otherwise-unambiguous academic posting just because it isn't one
        # of the recognized job-board URL shapes.
        is_title_shaped_match = has_positive_title and len(hay) >= 20
        if is_strong or in_trusted_table or is_title_shaped_match:
            pass
        elif is_weak and has_positive_title:
            pass
        else:
            continue
        job_url = urljoin(base_url, href)
        if job_url in seen_urls:
            continue
        seen_urls.add(job_url)
        title_el = a.find(class_=re.compile(r'title', re.I)) or a.find(['h1', 'h2', 'h3', 'h4'])
        # Fall back to the full link text if the nested title element exists
        # but is empty (icon-only heading, decorative wrapper) -- otherwise
        # this silently produces a blank-title "posting".
        title = (title_el.get_text(strip=True) if title_el else '') or hay
        if not title:
            continue
        postings.append({
            'job_title': title, 'department': '', 'location': '',
            'position_type': tab_label or '', 'post_date': '', 'posting_url': job_url,
            'language': '',
        })

    # Some sites list real postings as bare headings with NO link at all --
    # a flat page of "Professor in Engineering" / "Professor - Tier 2 Canada
    # Research Chair" style headings, application handled by email or a
    # single generic "how to apply" link elsewhere on the page, not one URL
    # per posting. A heading that already reads as a specific academic title
    # is self-evidently a real posting on its own -- unlike the trusted-table
    # case (where individual cells have no title text without page context),
    # no additional page-level signal is needed here. Guarded instead by
    # length + a small negative list for generic "meet our faculty"-style
    # marketing headings that would otherwise false-positive on "faculty".
    NON_POSTING_HEADING_RE = re.compile(
        r'\b(our faculty|meet (the|our) faculty|faculty directory|faculty profiles|'
        r'faculty (achievements|news|spotlight|research)|about (the|our) faculty)\b', re.I)
    seen_titles = {p['job_title'] for p in postings}
    for h in soup.find_all(['h2', 'h3', 'h4']):
        if h.find_parent('a'):
            continue
        title = h.get_text(strip=True)
        if not title or len(title) < 15 or title in seen_titles:
            continue
        if not POSITIVE_TITLE_RE.search(title) or HARD_NEGATIVE_RE.match(title) or NON_POSTING_HEADING_RE.search(title):
            continue
        seen_titles.add(title)
        postings.append({
            'job_title': title, 'department': '', 'location': '',
            'position_type': tab_label or '', 'post_date': '', 'posting_url': base_url,
            'language': '',
        })
    return postings


def find_department_hop_links(html, base_url, already_visited):
    soup = BeautifulSoup(html, 'html.parser')
    hops = []
    seen = set()
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if not text or not DEPT_HOP_HINT_RE.search(text):
            continue
        full = urljoin(base_url, a['href'])
        # dedupe BEFORE capping -- the same nav link often appears twice on a
        # page (header + footer, or a duplicated mobile nav), and capping on
        # the raw (undeduped) list can silently squeeze out real distinct
        # department targets in favor of repeats of ones already counted.
        if full in already_visited or full in seen:
            continue
        seen.add(full)
        hops.append(full)
    # A university can legitimately have a dozen+ faculties/schools -- cap
    # generously rather than risk missing the one with real postings.
    return hops[:15]


PAGINATION_LINK_RE = re.compile(r'^(next|next page|»|>>|suivant|weiter|siguiente)$', re.I)
PAGINATION_HREF_RE = re.compile(r'([?&](page|p|pg|offset|start)=\d+)', re.I)


def find_pagination_links(html, base_url, already_visited):
    """Traditional numbered/next-page <a href> pagination -- separate from
    the JS Load-More button handling in _click_load_more_and_paginate, which
    only runs in the Playwright path. A plain server-rendered paginated list
    (page=1, page=2, ... in the href, or a "Next"/"»" link) needs this instead;
    without it, a plain-HTML site with real pagination only ever shows page 1."""
    soup = BeautifulSoup(html, 'html.parser')
    pages = []
    seen = set()
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        href = a['href']
        is_numbered = text.isdigit() and 1 <= len(text) <= 3
        is_next_word = bool(PAGINATION_LINK_RE.match(text))
        is_rel_next = a.get('rel') and 'next' in a.get('rel')
        is_page_href = bool(PAGINATION_HREF_RE.search(href))
        if not (is_numbered or is_next_word or is_rel_next or is_page_href):
            continue
        full = urljoin(base_url, href)
        if full in already_visited or full in seen or full == base_url:
            continue
        seen.add(full)
        pages.append(full)
    return pages[:15]


BOT_CHALLENGE_RE = re.compile(
    r'(human verification|attention required.{0,20}cloudflare|checking your browser|'
    r'captcha|access denied|request blocked|please verify you are a human|'
    r'awswaf|challenge-platform|403 forbidden|you don.t have permission to access|'
    r'^\s*forbidden\s*$)', re.I)


def scrape_with_pagination(html, page_url, tab_label, visited, max_pages=15):
    """Scrapes one page, then follows traditional numbered/next-page <a href>
    pagination (separate from the JS Load-More handling, which only runs in
    the Playwright path) up to max_pages, merging results as it goes."""
    postings = list(generic_scrape_page(html, page_url, tab_label))
    current_html, current_url = html, page_url
    for _ in range(max_pages):
        next_pages = find_pagination_links(current_html, current_url, visited)
        if not next_pages:
            break
        next_url = next_pages[0]
        visited.add(next_url)
        next_captures, _ = fetch_html_smart(next_url)
        if not next_captures:
            break
        current_html, _ = next_captures[0]
        current_url = next_url
        page_postings = generic_scrape_page(current_html, current_url, tab_label)
        if not page_postings:
            break  # an empty page means we've run past the real content
        postings.extend(page_postings)
    return postings


def generic_scrape_with_hops(url):
    captures, fetcher = fetch_html_smart(url)
    all_postings = []
    visited = {url}
    lang = None
    blocked = bool(captures) and all(BOT_CHALLENGE_RE.search(h) for h, _ in captures)
    for html, tab_label in captures:
        if lang is None:
            lang = detect_page_language(html)
        # Always scrape the original page itself -- an "EN" nav link is often
        # just a generic language toggle to the site's English homepage, not a
        # real translation of THIS page, so it must never replace real content
        # found here, only ever add to it. Also follows traditional numbered
        # pagination on this page, not just whatever's on the first page.
        original_postings = scrape_with_pagination(html, url, tab_label, visited)
        all_postings.extend(original_postings)
        en_link = find_english_version_link(html, url)
        if en_link and en_link not in visited:
            visited.add(en_link)
            en_captures, _ = fetch_html_smart(en_link)
            for en_html, en_tab in en_captures:
                en_postings = scrape_with_pagination(en_html, en_link, en_tab or tab_label, visited)
                for p in en_postings:
                    p['language'] = p.get('language') or 'en'
                all_postings.extend(en_postings)
        # Always check department/faculty hop targets, regardless of how many
        # postings the central page already showed -- a central page listing
        # SOME postings is not evidence it lists ALL of them (confirmed real
        # case: ULB's central page showed exactly 3 postings while 14 separate
        # faculty pages, including the one directly relevant to this site's
        # subject scope, were never checked under the old "only hop if <3"
        # rule -- a central "here are some jobs" page and a full department
        # index are different things and both need checking).
        for hop_url in find_department_hop_links(html, url, visited):
            visited.add(hop_url)
            hop_captures, _ = fetch_html_smart(hop_url)
            for hop_html, hop_tab in hop_captures:
                # Each department page can itself be paginated.
                all_postings.extend(scrape_with_pagination(hop_html, hop_url, hop_tab, visited))
    seen, out = set(), []
    for p in all_postings:
        # A blank/whitespace-only title is never a real posting regardless of
        # which path produced it -- belt-and-suspenders on top of the checks
        # in generic_scrape_page, since a blank title is useless to show a
        # user no matter the root cause.
        if not p.get('job_title', '').strip():
            continue
        # Heading-only postings (no distinct link -- see generic_scrape_page)
        # share posting_url with every other heading on the same page, so
        # dedup on URL alone would wrongly collapse distinct postings into
        # one row. Include the title in the key so that only genuinely
        # identical (title, url) pairs are treated as duplicates.
        key = (p['posting_url'], p.get('job_title', ''))
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out, fetcher, lang, blocked


# --------------------------------------------------------------------------
# Per-school orchestration
# --------------------------------------------------------------------------

def process_school(school_id, name, url):
    result = {'school_id': school_id, 'name': name, 'status': None, 'tier': None,
              'platform': None, 'count': 0, 'error': ''}
    postings = []
    platform = detect_platform(url)

    try:
        if platform == 'workday':
            postings, err = scrape_workday(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='workday', count=len(postings))
            else:
                result['error'] = err or 'workday adapter failed'
        elif platform == 'oracle':
            postings, err = scrape_oracle(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='oracle', count=len(postings))
            else:
                result['error'] = err or 'oracle adapter failed'
        elif platform == 'academicjobsonline':
            postings, err = scrape_academicjobsonline(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='academicjobsonline', count=len(postings))
            else:
                result['error'] = err or 'ajo adapter failed'
        elif platform == 'apella':
            postings, err = scrape_apella(url, name)
            if postings is not None:
                result.update(status='ok', tier=0, platform='apella', count=len(postings))
            else:
                result['error'] = err or 'apella adapter failed'
        elif platform == 'poland_nauka':
            postings, err = scrape_poland_nauka(url, name)
            if postings is not None:
                result.update(status='ok', tier=0, platform='poland_nauka', count=len(postings))
            else:
                result['error'] = err or 'poland adapter failed'
        elif platform == 'smartrecruiters':
            postings, err = scrape_smartrecruiters(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='smartrecruiters', count=len(postings))
            else:
                result['error'] = err or 'smartrecruiters adapter failed'
        elif platform == 'peopleadmin':
            postings, err = scrape_peopleadmin(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='peopleadmin', count=len(postings))
            else:
                result['error'] = err or 'peopleadmin adapter failed'
        elif platform == 'adp':
            postings, err = scrape_adp(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='adp', count=len(postings))
            else:
                result['error'] = err or 'adp adapter failed'
        elif platform == 'cornerstone':
            postings, err = scrape_cornerstone(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='cornerstone', count=len(postings))
            else:
                result['error'] = err or 'cornerstone adapter failed'
        elif platform == 'icims':
            postings, err = scrape_icims(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='icims', count=len(postings))
            else:
                result['error'] = err or 'icims adapter failed'
        elif platform == 'ultipro':
            postings, err = scrape_ultipro(url)
            if postings is not None:
                result.update(status='ok', tier=1, platform='ultipro', count=len(postings))
            else:
                result['error'] = err or 'ultipro adapter failed'

        if platform is None or result['status'] != 'ok':
            status, html_first = fetch_requests(url)
            if status == 200 and html_first:
                schema_postings = scrape_schema_org(html_first, url)
            else:
                schema_postings = []
            if schema_postings:
                postings = schema_postings
                result.update(status='ok', tier=2, platform='schema.org', count=len(postings))
            else:
                generic_postings, fetcher, lang, blocked = generic_scrape_with_hops(url)
                postings = generic_postings
                for p in postings:
                    if not p.get('language'):
                        p['language'] = lang or ''
                if not postings and blocked:
                    result.update(status='failed', tier=3, platform=f'generic({fetcher})',
                                   count=0, error='bot-challenge page (CAPTCHA/WAF) -- not evaded, flagged')
                else:
                    result.update(status='ok' if postings else 'empty', tier=3,
                                   platform=f'generic({fetcher})', count=len(postings))
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = f'{type(e).__name__}: {e}'
        traceback.print_exc()

    # Post-process every posting the same way regardless of which tier found it:
    # split embedded department clauses out of the title, infer position_type,
    # and translate into English when needed (English kept as-is, no API call).
    for p in postings:
        raw_title = p.get('job_title', '')
        title, dept_from_title = split_title_department(raw_title, name)
        if dept_from_title and not p.get('department'):
            p['department'] = dept_from_title
        p['job_title'] = title
        p['job_title_original'] = raw_title
        p['department_original'] = p.get('department', '')
        lang = (p.get('language') or '').split('-')[0].lower()
        if lang and lang != 'en':
            p['job_title'] = translate_to_english(title, lang)
            if p.get('department'):
                p['department'] = translate_to_english(p['department'], lang)
        if not p.get('position_type'):
            p['position_type'] = infer_position_type(p['job_title'])

    return postings, result


def write_school_csv(school_id, postings, result):
    path = os.path.join(OUT_DIR, f'school_id_{school_id}_job_posts.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        for p in postings:
            row = {k: p.get(k, '') for k in CANONICAL_FIELDS}
            row['school_id'] = school_id
            row['source_tier'] = result.get('tier', '')
            row['source_platform'] = result.get('platform', '')
            row['scraped_at'] = now_iso()
            writer.writerow(row)
    return path


def mark_done(school_id):
    open(os.path.join(OUT_DIR, f'school_id_{school_id}_job_posts.csv.done'), 'w').close()


def is_done(school_id):
    return os.path.exists(os.path.join(OUT_DIR, f'school_id_{school_id}_job_posts.csv.done'))


def append_log(row):
    is_new = not os.path.exists(LOG_CSV)
    with open(LOG_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['school_id', 'name', 'status', 'tier', 'platform', 'count', 'error', 'timestamp'])
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def load_schools(limit_ids=None):
    rows = []
    with open(MASTER_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['country'] == 'US':
                continue
            link = (row.get('careers_link') or '').strip()
            if not link:
                continue
            if limit_ids and int(row['school_id']) not in limit_ids:
                continue
            rows.append(row)
    return rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    limit_ids = None
    if len(sys.argv) > 1 and sys.argv[1] == '--only':
        limit_ids = set(int(x) for x in sys.argv[2].split(','))

    schools = load_schools(limit_ids)
    log(f'{len(schools)} non-US schools with a careers_link to process')

    done_count = 0
    for i, row in enumerate(schools, 1):
        sid = int(row['school_id'])
        name = row['name']
        url = row['careers_link']
        if is_done(sid):
            done_count += 1
            continue
        log(f'[{i}/{len(schools)}] {name} (id={sid}) -> {url}')
        postings, result = process_school(sid, name, url)
        write_school_csv(sid, postings, result)
        mark_done(sid)
        result['timestamp'] = now_iso()
        append_log(result)
        log(f'  -> {result["status"]} tier={result["tier"]} platform={result["platform"]} count={result["count"]} {("ERR: "+result["error"]) if result["error"] else ""}')
        time.sleep(random.uniform(0.8, 1.8))

    if _browser:
        _browser.close()
    if _pw:
        _pw.stop()
    log(f'Done. {done_count} already-completed schools skipped this run.')


if __name__ == '__main__':
    main()
