"""
Self-contained engine behind every school_id_<id>_job_postings.py script in
school_job_posts_code/. Does NOT import scrape_job_postings.py -- that
pipeline's own one-size-fits-all generic heuristics missed real postings
often enough that per-school customization is the entire point of this
rewrite. What's reused from it is only *knowledge* of how each ATS
platform's underlying API works (worked out and debugged there, especially
Oracle's session-capture trick and Workday's facet handling) -- each
adapter below is a fresh, independent implementation informed by that, not
a call into that file.

Two very different kinds of school use this module:

1. Schools on a shared ATS PLATFORM (Workday, Oracle Cloud HCM, Taleo,
   Cornerstone, PeopleAdmin, ADP, iCIMS, Ultipro, SmartRecruiters,
   AcademicJobsOnline, Apella, Poland's national portal). Every school on
   the same platform runs the exact same underlying site software, so
   sharing one adapter per platform is real code reuse, not the
   one-size-fits-all problem -- a per-school script for one of these just
   calls run_platform_school().

2. "Own website" schools (the majority -- no two alike). These get NO
   shared scraping logic here. Each per-school script defines its own
   find_links() function, using only the low-level building blocks below
   (fetch_static, fetch_rendered, extract_links) and then calls
   run_checkpointed() to merge the result into its own checkpoint/CSV. Open
   any one school's file to see and edit exactly how ITS postings are
   found, with zero effect on any other school.

Output: school_job_posts/school_id_<id>_job_posts.csv -- two columns
(school_id, post_link).

Checkpoint: school_id_<id>_job_postings.checkpoint (JSON), saved next to
the per-school script. `links` only ever grows -- a link found once stays
until the checkpoint is deleted by hand. A run that starts against a
checkpoint left 'in_progress' (the previous run was killed) is free to
retry from scratch at the platform-adapter/whole-page level -- true
mid-page resume is each script's own business if it chooses to track more
detailed progress; run_checkpointed only guarantees no *already-found* link
is ever lost across runs, and that a total connection failure is recorded
as 'error', never silently read back as "confirmed zero postings".
"""
import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse, urlsplit, urljoin, parse_qs

import requests
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'school_job_posts')

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

_pw = None
_browser = None


def get_browser():
    global _pw, _browser
    if _browser is None and sync_playwright is not None:
        _pw = sync_playwright().start()
        _browser = _pw.chromium.launch()
    return _browser


def close_browser():
    global _pw, _browser
    if _browser:
        _browser.close()
        _browser = None
    if _pw:
        _pw.stop()
        _pw = None


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


# --------------------------------------------------------------------------
# Low-level fetch / extraction toolbox. Shared because it's genuinely
# generic (an HTTP GET, a rendered page load, a plain link scan) -- it makes
# no decisions about what counts as a posting on any particular school's
# page. Every own-website per-school script builds its own find_links() out
# of these.
# --------------------------------------------------------------------------

def fetch_static(url, method='GET', json_body=None, timeout=20, extra_headers=None):
    """Plain HTTP request, no JS. Returns (status_code_or_None, text)."""
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


def fetch_rendered(url, wait_ms=2000, actions=None, timeout=25000):
    """Loads url in a real browser and returns the rendered HTML. Pass
    `actions` (a function of one argument, the Playwright page) for a
    school-specific interaction -- click a tab, scroll until a sentinel
    disappears, page through results -- run after the initial load and
    before the HTML is read back. Returns a short 'FETCH_FAILURE: ...'
    string (check with is_fetch_failure()) if the page can't be reached, or
    '' if Playwright itself isn't available."""
    b = get_browser()
    if b is None:
        return ''
    page = b.new_page(user_agent=UA)
    try:
        page.goto(url, timeout=timeout, wait_until='domcontentloaded')
        page.wait_for_timeout(wait_ms)
        if actions:
            actions(page)
        return page.content()
    except Exception as e:
        return f'FETCH_FAILURE: {e}'
    finally:
        page.close()


_FETCH_FAILURE_RE = re.compile(
    r'(connection refused|max retries exceeded|failed to establish a new connection|'
    r'name or service not known|connection reset by peer|read timed out|'
    r'nodename nor servname provided|net::err_|timeout \d+ms exceeded|fetch_failure:)', re.I)


def is_fetch_failure(html):
    """True if `html` is actually a swallowed connection error, not real
    (possibly genuinely empty) page content. Distinguishes "couldn't reach
    the site, this should be retried" from "reached it, found nothing" --
    confirmed necessary live: a blocked/unreachable site otherwise reads as
    a normal empty page and gets checkpointed as a false verified zero."""
    return bool(html) and len(html) < 2000 and bool(_FETCH_FAILURE_RE.search(html))


def extract_links(html, base_url, href_pattern=None, text_pattern=None):
    """Every distinct <a href> on the page, resolved to an absolute URL,
    excluding anchors/mailto/javascript. With neither pattern given this is
    deliberately a wide net -- every link on the page -- meant as a
    starting point for a school-specific filter, not a universal answer.
    Pass href_pattern and/or text_pattern (compiled regexes) to narrow it;
    a link is kept if either one matches."""
    soup = BeautifulSoup(html, 'html.parser')
    out, seen = [], set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:')):
            continue
        full = urljoin(base_url, href)
        if full in seen:
            continue
        if href_pattern or text_pattern:
            text = a.get_text(' ', strip=True)
            if not ((href_pattern and href_pattern.search(href)) or
                    (text_pattern and text_pattern.search(text))):
                continue
        seen.add(full)
        out.append(full)
    return out


# A reasonable starting filter for extract_links(href_pattern=...) -- NOT
# baked into extract_links itself, just offered here so a per-school
# find_links() isn't forced to invent this from nothing. Loosen, tighten, or
# ignore entirely per school.
COMMON_JOB_URL_HINTS = re.compile(
    r'(job|career|vacanc|posit|posting|requisition|opening|emploi|stelle|empleo|lavoro|vaga|'
    r'oferta|ogloszenie)', re.I)


# --------------------------------------------------------------------------
# Checkpoint / CSV I/O
# --------------------------------------------------------------------------

def load_checkpoint(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_checkpoint(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def write_posts_csv(school_id, links):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f'school_id_{school_id}_job_posts.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['school_id', 'post_link'])
        for link in links:
            w.writerow([school_id, link])
    return path


def _add_links(ckpt, new_urls):
    seen = set(ckpt['links'])
    added = False
    for u in new_urls:
        u = (u or '').strip()
        if u and u not in seen:
            seen.add(u)
            ckpt['links'].append(u)
            added = True
    return added


# --------------------------------------------------------------------------
# Checkpoint-driven orchestration. Generic on purpose: it only merges
# whatever find_links_fn() returns into the checkpoint/CSV and records
# success or failure. It never decides HOW to find links -- that's each
# script's own find_links_fn.
# --------------------------------------------------------------------------

def run_checkpointed(school_id, checkpoint_path, find_links_fn):
    """find_links_fn: a zero-argument callable, owned entirely by the
    calling per-school script, that returns a list of posting-URL strings
    or raises on failure. Every own-website script's find_links() and every
    platform adapter below is called through this."""
    ckpt = load_checkpoint(checkpoint_path)
    ckpt.setdefault('links', [])
    ckpt['school_id'] = school_id
    ckpt['status'] = 'in_progress'
    ckpt['updated_at'] = now_iso()
    ckpt.setdefault('started_at', now_iso())
    save_checkpoint(checkpoint_path, ckpt)
    try:
        links = find_links_fn()
        _add_links(ckpt, links)
        ckpt['status'] = 'complete'
        ckpt['completed_at'] = now_iso()
        ckpt['last_error'] = ''
    except Exception as e:
        ckpt['status'] = 'error'
        ckpt['last_error'] = f'{type(e).__name__}: {e}'
    finally:
        ckpt['updated_at'] = now_iso()
        save_checkpoint(checkpoint_path, ckpt)
        write_posts_csv(school_id, ckpt['links'])
    return ckpt


# ==========================================================================
# Platform adapters -- one per shared ATS platform. Each takes the school's
# careers_link (+ name where the platform needs it to disambiguate a
# shared/multi-tenant site) and returns a plain list of posting URLs, or
# raises on failure. Ported from scrape_job_postings.py's already-debugged
# understanding of each platform's real API, written fresh here.
# ==========================================================================

def detect_platform(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if 'myworkdayjobs.com' in host or 'myworkdaysite.com' in host:
        return 'workday'
    if 'oraclecloud.com' in host:
        return 'oracle'
    # Some Oracle Cloud HCM instances run on a white-labeled custom domain
    # instead of an oraclecloud.com host (confirmed live: Northumbria
    # University's work4.northumbria.ac.uk) -- the path/fragment still
    # carries Oracle's own "/hcmUI/CandidateExperience/.../sites/<id>/jobs"
    # signature regardless of domain, which scrape_oracle already targets.
    if re.search(r'/hcmUI/CandidateExperience/', url, re.I) or re.search(r'/sites/[^/]+/jobs\b', url, re.I):
        return 'oracle'
    if 'taleo.net' in host:
        return 'taleo'
    if 'academicjobsonline.org' in host:
        return 'academicjobsonline'
    if 'apella.minedu.gov.gr' in host:
        return 'apella'
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
    if host == 'my.corehr.com':
        return 'corehr'
    return None


def _resolve_workday_facet_by_name(api, school_name):
    """Some Workday links reference a facet selection ("/refreshFacet/<id>")
    that isn't resolvable from the URL alone on a shared multi-tenant site
    -- falls back to matching the school's own name against the tenant's
    facet value list."""
    status, text = fetch_static(api, method='POST', json_body={
        'appliedFacets': {}, 'limit': 1, 'offset': 0, 'searchText': ''
    })
    if status != 200:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    name_words = [w.lower() for w in re.split(r'\s+', school_name or '') if len(w) > 3]
    if not name_words:
        return None
    for facet in data.get('facets', []):
        param = facet.get('facetParameter')
        if not param:
            continue
        for v in facet.get('values', []):
            descriptor = (v.get('descriptor') or '').lower()
            if all(w in descriptor for w in name_words):
                return param, v.get('id')
    return None


def scrape_workday(url, school_name=None):
    parsed = urlparse(url)
    host_parts = parsed.netloc.split('.')
    path_parts = [p for p in parsed.path.split('/') if p]
    path_parts = [p for p in path_parts if not re.fullmatch(r'[a-z]{2}(-[A-Z]{2})?', p)]
    if 'myworkdaysite.com' in parsed.netloc:
        # Newer Workday "Career Site" URL scheme -- confirmed live on
        # Federation University: host is just "wd105.myworkdaysite.com"
        # (no tenant subdomain), and tenant/site instead come from the
        # PATH ("/recruiting/<tenant>/<site>"). The real API, captured via
        # network trace, is still /wday/cxs/<tenant>/<site>/jobs -- same
        # endpoint shape as the older scheme, just a different place to
        # read tenant/site from.
        if len(path_parts) < 2:
            raise RuntimeError('unrecognized myworkdaysite.com path -- expected /recruiting/<tenant>/<site>')
        tenant, site = path_parts[-2], path_parts[-1]
    else:
        if len(host_parts) < 4:
            raise RuntimeError('unrecognized workday host')
        tenant = host_parts[0]
        if not path_parts:
            raise RuntimeError('no site in workday path')
        site = path_parts[0]
    api = f'https://{parsed.netloc}/wday/cxs/{tenant}/{site}/jobs'

    NON_FACET_PARAMS = {'lastselectedfacet', 'mode', 'source', 'query', 'q'}
    applied_facets = {}
    for key, values in parse_qs(parsed.query).items():
        if key.lower() in NON_FACET_PARAMS or key.lower().startswith('selected'):
            continue
        applied_facets[key] = values
    if not applied_facets and re.search(r'/refreshFacet/', parsed.path, re.I):
        resolved = _resolve_workday_facet_by_name(api, school_name) if school_name else None
        if resolved:
            param, facet_id = resolved
            applied_facets = {param: [facet_id]}
        else:
            raise RuntimeError('workday: facet in URL not resolvable from URL or school name')

    links, offset, limit, total = [], 0, 20, None
    for _ in range(60):
        status, text = fetch_static(api, method='POST', json_body={
            'appliedFacets': applied_facets, 'limit': limit, 'offset': offset, 'searchText': ''
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
            links.append(urljoin(f'https://{parsed.netloc}', j.get('externalPath', '')))
        offset += limit
        if total is not None and offset >= total:
            break
        time.sleep(0.3)
    return links


def scrape_oracle(url):
    """Oracle Recruiting Cloud requires session state a plain request can't
    fake (cookies set via the page's own JS, not simple Set-Cookie headers,
    plus specific headers). Load the page once via Playwright to capture the
    exact headers/cookies its own first API request used, then replay that
    session via plain requests for the remaining paginated calls."""
    parsed = urlparse(url)
    m = re.search(r'/sites/([^/]+)', parsed.path)
    site_number = m.group(1) if m else None
    base = f'https://{parsed.netloc}'

    b = get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    captured = {}
    for attempt in range(2):
        captured = {}
        page = None
        try:
            page = b.new_page(user_agent=UA)

            def on_request(req):
                if 'recruitingCEJobRequisitions' in req.url and not captured:
                    captured['headers'] = dict(req.headers)
                    captured['url'] = req.url

            page.on('request', on_request)
            with page.expect_request('**/recruitingCEJobRequisitions**', timeout=15000):
                page.goto(url, timeout=25000, wait_until='domcontentloaded')
            page.wait_for_timeout(500)
            captured['cookies'] = page.context.cookies()
            break
        except Exception as e:
            last_err = e
        finally:
            if page:
                page.close()
    else:
        raise RuntimeError(f'oracle session capture failed: {last_err}')

    if 'headers' not in captured or 'url' not in captured:
        raise RuntimeError('oracle: could not capture a real session')
    session_headers = dict(captured['headers'])
    session_headers['Cookie'] = '; '.join(f"{c['name']}={c['value']}" for c in captured['cookies'])
    session_headers.pop('cookie', None)
    if 'offset=' in captured['url']:
        base_api_url = re.sub(r'offset=\d+', 'offset={offset}', captured['url'])
    else:
        base_api_url = captured['url'] + ',offset={offset}'

    links, offset, limit = [], 0, 25
    for _ in range(20):
        api = base_api_url.format(offset=offset)
        status, text = fetch_static(api, extra_headers=session_headers)
        if status != 200:
            break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            break
        items = data.get('items', [])
        reqs = items[0].get('requisitionList', []) if items else []
        if not reqs:
            break
        for r in reqs:
            links.append(urljoin(base, f"/hcmUI/CandidateExperience/en/sites/{site_number or 'CX_1'}/job/{r.get('Id','')}"))
        offset += limit
        if len(reqs) < limit:
            break
        time.sleep(0.3)
    return links


def scrape_cornerstone(url):
    """Cornerstone OnDemand (*.csod.com) calls a real JSON API but needs a
    session-scoped Bearer JWT issued by the page's own JS -- captured once
    via Playwright, then replayed with plain requests."""
    b = get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    captured = {}
    page = None
    try:
        page = b.new_page(user_agent=UA)

        def on_request(req):
            if 'rec-job-search/external/jobs' in req.url and not captured:
                auth = req.headers.get('authorization')
                if auth:
                    captured['auth'] = auth
                    captured['api_host'] = urlparse(req.url).netloc
                    try:
                        body = json.loads(req.post_data or '{}')
                        captured['careerSiteId'] = body.get('careerSiteId')
                        captured['careerSitePageId'] = body.get('careerSitePageId')
                        captured['cultureId'] = body.get('cultureId', 1)
                        captured['cultureName'] = body.get('cultureName', 'en-US')
                    except (json.JSONDecodeError, TypeError):
                        pass

        page.on('request', on_request)
        with page.expect_request('**/rec-job-search/external/jobs', timeout=15000):
            page.goto(url, timeout=25000, wait_until='networkidle')
        page.wait_for_timeout(500)
    except Exception as e:
        raise RuntimeError(f'cornerstone token capture failed: {e}')
    finally:
        if page:
            page.close()

    if 'auth' not in captured or captured.get('careerSiteId') is None:
        raise RuntimeError('cornerstone auth token not captured')

    host = urlparse(url).netloc
    api = f'https://{captured["api_host"]}/rec-job-search/external/jobs'
    headers = {
        'Authorization': captured['auth'], 'Content-Type': 'application/json',
        'Origin': f'https://{host}', 'Referer': f'https://{host}/', 'User-Agent': UA,
    }
    links, page_num, total = [], 1, None
    for _ in range(40):
        payload = {
            'careerSiteId': captured['careerSiteId'], 'careerSitePageId': captured['careerSitePageId'],
            'pageNumber': page_num, 'pageSize': 25, 'cultureId': captured['cultureId'],
            'searchText': '', 'cultureName': captured['cultureName'], 'states': [], 'countryCodes': [],
            'cities': [], 'placeID': '', 'radius': None, 'postingsWithinDays': None,
            'customFieldCheckboxKeys': [], 'customFieldDropdowns': [], 'customFieldRadios': [],
        }
        status, text = fetch_static(api, method='POST', json_body=payload, extra_headers=headers)
        if status != 200:
            break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            break
        reqs = data.get('data', {}).get('requisitions', [])
        if total is None:
            total = data.get('data', {}).get('totalCount', 0)
        if not reqs:
            break
        for r in reqs:
            links.append(f'https://{host}/ux/ats/careersite/{captured["careerSitePageId"]}/requisition/{r.get("requisitionId")}')
        page_num += 1
        if len(links) >= total:
            break
        time.sleep(0.3)
    return links


def scrape_peopleadmin(url):
    """Any *.peopleadmin.<tld> instance exposes a stable Atom feed at
    /postings/all_jobs.atom regardless of the specific institution."""
    parsed = urlparse(url)
    api = f'https://{parsed.netloc}/postings/all_jobs.atom'
    status, text = fetch_static(api)
    if status != 200:
        raise RuntimeError(f'peopleadmin atom status={status}')
    soup = BeautifulSoup(text, 'xml')
    links = []
    for entry in soup.find_all('entry'):
        link_tag = entry.find('link')
        if link_tag and link_tag.has_attr('href'):
            links.append(link_tag['href'])
    return links


def scrape_adp(url):
    """ADP Workforce Now recruitment pages are a JS SPA calling a public
    JSON API keyed by the `cid` query param already in the careers link. No
    per-job URL is exposed in the API, so every posting shares the search
    page URL -- honest given what the platform actually exposes."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    cid = (qs.get('cid') or [None])[0]
    if not cid:
        raise RuntimeError('no cid param in adp url')
    api = (f'https://{parsed.netloc}/mascsr/default/careercenter/public/events/'
           f'staffing/v1/job-requisitions?cid={cid}&timeStamp={int(time.time()*1000)}')
    status, text = fetch_static(api, extra_headers={'Accept': 'application/json'})
    if status != 200:
        raise RuntimeError(f'adp api status={status}')
    data = json.loads(text)
    return [url for _ in data.get('jobRequisitions', [])]


_ICIMS_JOB_HREF_RE = re.compile(r'/jobs/\d+/')


def scrape_icims(url):
    """iCIMS nests the real listing in a nested <iframe>, not the top-level
    document -- fetch_rendered's returned html is always page.content(),
    which is the OUTER shell only (generic site nav, no postings), so a
    plain extract_links() on it finds nothing real regardless of pattern.
    Confirmed live (IE University): the real listing lives in page.frames[1].

    Also confirmed live: the search page shows "Please Enable Cookies to
    Continue" on a first-ever visit and only renders real content once
    cookies set on that first visit are present -- i.e. it needs to be
    loaded TWICE in the same browser context, not once.

    Pagination links inside that frame ("...jobs/search?pr=<n>&in_iframe=1")
    are real, plain hrefs -- no click needed, so remaining pages are
    fetched directly via fetch_static rather than more browser navigation."""
    parsed = urlparse(url)
    search_url = f'https://{parsed.netloc}/jobs/search?ss=1'

    b = get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    page = b.new_page(user_agent=UA)
    try:
        page.goto(search_url, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        page.goto(search_url, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(4000)
        if len(page.frames) < 2:
            raise RuntimeError('icims: expected nested job-listing frame not found')
        html = page.frames[1].content()
    finally:
        page.close()

    links, seen = [], set()

    def collect(page_html):
        soup = BeautifulSoup(page_html, 'html.parser')
        added = False
        for a in soup.find_all('a', href=True):
            if not _ICIMS_JOB_HREF_RE.search(a['href']):
                continue
            full = urljoin(search_url, a['href'].split('?')[0])
            if full not in seen:
                seen.add(full)
                links.append(full)
                added = True
        return added

    collect(html)
    for page_num in range(1, 20):
        page_url = f'https://{parsed.netloc}/jobs/search?pr={page_num}&in_iframe=1'
        status, text = fetch_static(page_url)
        if status != 200 or not text or not collect(text):
            break
        time.sleep(0.3)
    return links


def scrape_ultipro(url):
    """UKG/Ultipro job boards call a real public JSON API keyed by the
    tenant/board path already in the careers link, no auth needed."""
    parsed = urlparse(url)
    m = re.match(r'^(/[^/]+/JobBoard/[^/]+)/', parsed.path)
    if not m:
        raise RuntimeError('could not parse ultipro tenant/board path')
    api = f'https://{parsed.netloc}{m.group(1)}/JobBoardView/LoadSearchResults'
    links, skip, top, total = [], 0, 50, None
    for _ in range(40):
        payload = {
            'opportunitySearch': {'Top': top, 'Skip': skip, 'QueryString': '',
                                   'OrderBy': [{'Value': 'postedDateDesc', 'PropertyName': 'PostedDate', 'Ascending': False}],
                                   'Filters': []},
            'matchCriteria': {'PreferredJobs': [], 'Educations': [], 'LicenseAndCertifications': [],
                               'Skills': [], 'hasNoLicenses': False, 'SkippedSkills': []},
        }
        status, text = fetch_static(api, method='POST', json_body=payload,
                                     extra_headers={'Accept': 'application/json'})
        if status != 200:
            break
        data = json.loads(text)
        if total is None:
            total = data.get('totalCount', 0)
        opps = data.get('opportunities', [])
        if not opps:
            break
        for o in opps:
            links.append(f'https://{parsed.netloc}{m.group(1)}/OpportunityDetail?opportunityId={o.get("Id","")}')
        skip += top
        if skip >= total:
            break
        time.sleep(0.3)
    return links


def scrape_smartrecruiters(url):
    """https://jobs.smartrecruiters.com/<Company>/... -> public REST API,
    api.smartrecruiters.com/v1/companies/<Company>/postings."""
    m = re.search(r'smartrecruiters\.com/([^/?#]+)', url)
    if not m:
        raise RuntimeError('could not parse smartrecruiters company slug')
    company = m.group(1)
    links, offset, limit = [], 0, 100
    for _ in range(10):
        api = f'https://api.smartrecruiters.com/v1/companies/{company}/postings?limit={limit}&offset={offset}'
        status, text = fetch_static(api, extra_headers={'Accept': 'application/json'})
        if status != 200:
            break
        data = json.loads(text)
        content = data.get('content', [])
        if not content:
            break
        for item in content:
            links.append(item.get('ref', '') or f'https://jobs.smartrecruiters.com/{company}/{item.get("id","")}')
        offset += limit
        if offset >= data.get('totalFound', 0):
            break
        time.sleep(0.3)
    return links


def scrape_academicjobsonline(url):
    status, html = fetch_static(url)
    if status != 200:
        raise RuntimeError(f'ajo fetch failed status={status}')
    return extract_links(html, 'https://academicjobsonline.org', href_pattern=re.compile(r'/jobs/'))


_APELLA_RSS_CACHE = None

def scrape_apella(url, school_name):
    global _APELLA_RSS_CACHE
    if _APELLA_RSS_CACHE is None:
        status, text = fetch_static('https://apella.minedu.gov.gr/apella-positions-rss.xml')
        if status != 200:
            raise RuntimeError(f'apella rss fetch failed status={status}')
        _APELLA_RSS_CACHE = text
    soup = BeautifulSoup(_APELLA_RSS_CACHE, 'xml')
    greek_name = GREEK_NAME_MAP.get(school_name)
    name_lower = (school_name or '').lower()
    links = []
    for item in soup.find_all('item'):
        creator = item.find('dc:creator')
        creator_text = creator.get_text(strip=True) if creator else ''
        if not creator_text:
            continue
        if greek_name and greek_name not in creator_text:
            continue
        if not greek_name and (not name_lower.split() or name_lower.split()[0] not in creator_text.lower()):
            continue
        link_tag = item.find('link')
        if link_tag:
            links.append(link_tag.get_text(strip=True))
    return links


GREEK_NAME_MAP = {
    'Athens University of Economics and Business': 'ΟΙΚΟΝΟΜΙΚΟ ΠΑΝΕΠΙΣΤΗΜΙΟ ΑΘΗΝΩΝ',
    'National Technical University of Athens': 'ΜΕΤΣΟΒΙΟ',
    'National and Kapodistrian University of Athens': 'ΚΑΠΟΔΙΣΤΡΙΑΚΟ',
    'Aristotle University of Thessaloniki': 'ΑΡΙΣΤΟΤΕΛΕΙΟ',
}

POLAND_NAME_MAP = {
    'AGH University of Krakow': 'Akademia Gorniczo-Hutnicza',
    'Jagiellonian University': 'Uniwersytet Jagiellonski',
    'University of Warsaw': 'Uniwersytet Warszawski',
    'Warsaw School of Economics': 'Szkola Glowna Handlowa',
}


def scrape_poland_nauka(url, school_name):
    base = 'https://bazaogloszen.nauka.gov.pl/wyniki-wyszukiwania/'
    keyword = POLAND_NAME_MAP.get(school_name, school_name)
    links, page_num = [], 1
    for _ in range(10):
        params_url = f'{base}?search_keywords={requests.utils.quote(keyword)}&search_per_page=50&search_page={page_num}'
        status, html = fetch_static(params_url)
        if status != 200:
            break
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_=re.compile(r'\bjob_listing\b'))
        if not articles:
            break
        for art in articles:
            title_a = art.select_one('.job-title a')
            if title_a and title_a.get('href'):
                links.append(title_a['href'])
        if len(articles) < 50:
            break
        page_num += 1
        time.sleep(0.3)
    return links


# --------------------------------------------------------------------------
# Taleo: covers both product UIs seen in this dataset.
#  - TBE ("...tbe.taleo.net/.../jobSearch?...")): a search-FORM page whose
#    "View All Postings" panel heading is static text -- the actual control
#    is the visible result-count link next to it (confirmed live on
#    Kwantlen: role=link name="view all postings" matches nothing, the
#    panel-count link is what navigates to results). Results then load via
#    scroll-triggered "jscroll": a sentinel <a class="jscroll-next"> that
#    throws "element is not visible" on a direct click -- it's meant to be
#    scrolled into view, not clicked -- appending 10 postings per batch
#    until the sentinel disappears.
#  - CareerSection ("...taleo.net/careersection/.../jobsearch.ftl"): a
#    search-form page with a "View All Jobs" link, then classic
#    REPLACE-per-page pagination behind an <a id="next"> control -- each
#    page's links must be captured before clicking Next (confirmed live on
#    CUHK: 99 postings recovered across 5 pages of ~25).
# --------------------------------------------------------------------------

TALEO_POSTING_HREF_RE = re.compile(r'(viewRequisition|applyRequisition|jobdetail\.ftl)', re.I)


def _canonical_taleo_link(href, base_url):
    """A single posting shows up behind several hrefs on the page (title
    link, "View" action, "Apply", sometimes a share-widget link with the
    real URL buried in a source= param) -- collapsed to one canonical URL
    per posting (by rid / by job id) so the CSV has one row per opening."""
    full = urljoin(base_url, href)
    parts = urlsplit(full)
    qs = parse_qs(parts.query)
    if 'rid' in qs:
        org = qs.get('org', [''])[0]
        cws = qs.get('cws', [''])[0]
        rid = qs['rid'][0]
        path = parts.path.rsplit('/', 1)[0] + '/viewRequisition'
        return f'{parts.scheme}://{parts.netloc}{path}?org={org}&cws={cws}&rid={rid}'
    if 'job' in qs:
        return f'{parts.scheme}://{parts.netloc}{parts.path}?job={qs["job"][0]}'
    return None


def _extract_taleo_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    out, seen = [], set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not TALEO_POSTING_HREF_RE.search(href):
            continue
        canon = _canonical_taleo_link(href, base_url)
        if canon and canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


def scrape_taleo(url):
    b = get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    page = b.new_page(user_agent=UA)
    links = []
    try:
        page.goto(url, timeout=25000, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)

        panel = page.locator('a.oracletaleocwsv2-panel-number')
        if panel.count() > 0:
            panel.first.click(timeout=5000)
            page.wait_for_timeout(2000)
        else:
            clicked = False
            try:
                vaj = page.get_by_text('View All Jobs', exact=False)
                if vaj.count() > 0 and vaj.first.is_visible():
                    vaj.first.click(timeout=5000)
                    page.wait_for_timeout(2500)
                    clicked = True
            except Exception:
                pass
            if not clicked:
                # A third TBE variant (confirmed live on HEC Montreal): no
                # panel-count link, no "View All Jobs" text -- just a plain
                # form Search submit button (onclick="checkForm(...)").
                # It's a real <button type="submit">, but Playwright's
                # normal .click() times out with "element is not visible"
                # no matter what (force=True included) -- it's genuinely
                # hidden until JS-triggered, not just off-screen. Dispatching
                # the click via page-context JS bypasses the visibility gate
                # entirely and reaches the same onclick handler a real
                # (CSS-shown) click would.
                try:
                    search_btn = page.locator('button.oracletaleocwsv2-btn-fa.fa-search.btn-primary')
                    if search_btn.count() > 0:
                        search_btn.first.evaluate('el => el.click()')
                        page.wait_for_timeout(2500)
                except Exception:
                    pass

        for _ in range(30):
            if page.locator('a.jscroll-next').count() == 0:
                break
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1200)
        seen = set()
        for l in _extract_taleo_links(page.content(), url):
            if l not in seen:
                seen.add(l)
                links.append(l)

        for _ in range(20):
            next_link = page.locator('#next')
            if next_link.count() == 0:
                break
            try:
                if next_link.first.get_attribute('aria-disabled') == 'true':
                    break
                next_link.first.click(timeout=5000)
            except Exception:
                break
            page.wait_for_timeout(2000)
            page_links = _extract_taleo_links(page.content(), url)
            if not page_links:
                for _ in range(3):
                    page.wait_for_timeout(1500)
                    page_links = _extract_taleo_links(page.content(), url)
                    if page_links:
                        break
                if not page_links:
                    break
            new_this_page = [l for l in page_links if l not in seen]
            for l in new_this_page:
                seen.add(l)
                links.append(l)
            if not new_this_page:
                break
    finally:
        page.close()
    return links


def scrape_corehr(url):
    """CoreHR (my.corehr.com/pls/<tenant>recruit/...) -- confirmed live on
    University of Oxford. The search-results page's job titles are
    javascript:viewTheJobSpec('<id>') handlers with no real href, but
    clicking one navigates to a real, directly-loadable (no session/cookie
    needed) detail URL built from that same id:
    .../erq_jobspec_version_4.display_form?p_company=<N>&...&
    p_recruitment_id=<id> -- confirmed by fetching that URL fresh via plain
    requests, no prior click. p_company is read from CAREERS_LINK's own
    query string rather than hardcoded, since it's tenant-specific."""
    parsed = urlparse(url)
    m = re.search(r'/pls/([^/]+)/', parsed.path)
    if not m:
        raise RuntimeError('could not parse corehr tenant from URL path')
    tenant = m.group(1)
    company = parse_qs(parsed.query).get('p_company', [''])[0]
    if not company:
        raise RuntimeError('no p_company param in corehr URL')
    html = fetch_rendered(url)
    if is_fetch_failure(html):
        raise RuntimeError(html)
    ids = sorted(set(re.findall(r"viewTheJobSpec\('(\d+)'\)", html)), key=int)
    base = f'https://{parsed.netloc}/pls/{tenant}/erq_jobspec_version_4.display_form'
    return [f'{base}?p_company={company}&p_internal_external=E&p_display_in_irish=N&'
            f'p_display_apply_ind=Y&p_recruitment_id={jid}' for jid in ids]


PLATFORM_ADAPTERS = {
    'workday': lambda url, name: scrape_workday(url, school_name=name),
    'corehr': lambda url, name: scrape_corehr(url),
    'oracle': lambda url, name: scrape_oracle(url),
    'taleo': lambda url, name: scrape_taleo(url),
    'cornerstone': lambda url, name: scrape_cornerstone(url),
    'peopleadmin': lambda url, name: scrape_peopleadmin(url),
    'adp': lambda url, name: scrape_adp(url),
    'icims': lambda url, name: scrape_icims(url),
    'ultipro': lambda url, name: scrape_ultipro(url),
    'smartrecruiters': lambda url, name: scrape_smartrecruiters(url),
    'academicjobsonline': lambda url, name: scrape_academicjobsonline(url),
    'apella': lambda url, name: scrape_apella(url, name),
    'poland_nauka': lambda url, name: scrape_poland_nauka(url, name),
}


def run_platform_school(school_id, name, careers_link, checkpoint_path, platform=None):
    """For a school on a known shared ATS platform. `platform` can be
    forced explicitly; otherwise detected from the URL."""
    platform = platform or detect_platform(careers_link)
    if platform not in PLATFORM_ADAPTERS:
        raise RuntimeError(f'no platform adapter for {platform!r}')
    adapter = PLATFORM_ADAPTERS[platform]

    def find_links():
        if not careers_link or not careers_link.strip():
            raise RuntimeError('no careers_link configured for this school')
        return adapter(careers_link, name)

    return run_checkpointed(school_id, checkpoint_path, find_links)
