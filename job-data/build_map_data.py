"""
Builds postings.json for the map's job search -- every scraped posting
joined to its school's coordinates, country and name.

Run from job-data/:  python3 build_map_data.py

WHY "available now" IS DEFINED AS "IN THE LATEST SCRAPE":
The obvious definition -- filter on the date a job was posted -- isn't
available. No source we scrape exposes a post date in any consistent
place (668 of the 771 Assistant Professor postings come from schools'
own websites, which share no convention), so job_info has no post_date
column to filter on. position_start_date exists but is populated on only
12% of Assistant Professor postings, because most postings simply never
state a start date; filtering on it would hide the other 88%.

What IS reliable is that every posting here was read off a live careers
page during the scrape: if a posting is in this file, the school was
advertising it at `scraped` time. So the map treats presence in the
latest scrape as "currently open", and exposes start date and application
deadline as OPTIONAL refinements, clearly marked as partial.

`first_seen` is carried per posting so that later scrapes can tell a new
posting from one that has been up for months, and so a posting that
disappears from its school's page can be aged out rather than lingering.
This first build backfills it from each school's scrape timestamp.
"""
import csv
import glob
import json
import os
import re
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INFO_DIR = os.path.join(HERE, 'school_job_info')
POSTS_CODE_DIR = os.path.join(HERE, 'school_job_posts_code')
OUT_PATH = os.path.join(ROOT, 'postings.json')

_MONTHS = ('january february march april may june july august september '
           'october november december').split()
_MONTH_NUM = {m: i + 1 for i, m in enumerate(_MONTHS)}
_MONTH_NUM.update({m[:3]: i + 1 for i, m in enumerate(_MONTHS)})

_ISO_RE = re.compile(r'\b(\d{4})-(\d{2})-(\d{2})\b')
_DMY_RE = re.compile(r'\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b')
_MDY_RE = re.compile(r'\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b')
_DMY_TEXT_RE = re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9}),?\s+(\d{4})\b')
_MY_RE = re.compile(r'\b([A-Za-z]{3,9})\s+(\d{4})\b')


def normalize_date(value):
    """Free text -> ISO 'YYYY-MM-DD', or '' when nothing parses. Postings
    write dates every way imaginable ("July 1, 2027", "31/03/2031",
    "1st September 2026", "Autumn 2027"); a month-and-year-only value is
    pinned to the 1st so it can still be range-filtered."""
    if not value:
        return ''
    text = value.strip()

    m = _ISO_RE.search(text)
    if m:
        return _safe_iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _MDY_RE.search(text)
    if m:
        month = _MONTH_NUM.get(m.group(1).lower()[:9]) or _MONTH_NUM.get(m.group(1).lower()[:3])
        if month:
            return _safe_iso(int(m.group(3)), month, int(m.group(2)))

    m = _DMY_TEXT_RE.search(text)
    if m:
        month = _MONTH_NUM.get(m.group(2).lower()[:9]) or _MONTH_NUM.get(m.group(2).lower()[:3])
        if month:
            return _safe_iso(int(m.group(3)), month, int(m.group(1)))

    m = _DMY_RE.search(text)
    if m:
        # day-first: every source using this form here is non-US
        return _safe_iso(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _MY_RE.search(text)
    if m:
        month = _MONTH_NUM.get(m.group(1).lower()[:9]) or _MONTH_NUM.get(m.group(1).lower()[:3])
        if month:
            return _safe_iso(int(m.group(2)), month, 1)
    return ''


def _safe_iso(year, month, day):
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return ''


def load_school_meta():
    """school_id -> {name, country, careers_link} from schools_master.csv."""
    meta = {}
    with open(os.path.join(HERE, 'schools_master.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                meta[int(row['school_id'])] = {
                    'name': row.get('name', ''),
                    'country': row.get('country', ''),
                }
            except (KeyError, TypeError, ValueError):
                continue
    return meta


def load_coords():
    """school_id -> (lat, lon, city) parsed out of the map page's own school
    arrays, so postings land on exactly the markers the map already uses
    rather than a second, possibly disagreeing, source of coordinates."""
    coords = {}
    with open(os.path.join(ROOT, 'index.html'), encoding='utf-8') as f:
        page = f.read()
    # Region comes from WHICH of the page's own arrays a school sits in,
    # rather than from a country->region table of our own. That way the jobs
    # filter and the existing Region / Area selects can never disagree about
    # where a school belongs.
    array_region = {
        'SCHOOLS': ('us', ''),
        'CANADA_SCHOOLS': ('canada', ''),
        'AUSTRALIA_SCHOOLS': ('australia', ''),
        'NEWZEALAND_SCHOOLS': ('newzealand', ''),
        'EUROPE_SCHOOLS': ('europe', ''),
        'HONGKONG_SCHOOLS': ('asia', 'hongkong'),
        'MACAU_SCHOOLS': ('asia', 'macau'),
        'SINGAPORE_SCHOOLS': ('asia', 'singapore'),
    }
    for m in re.finditer(r'const ([A-Z_]*SCHOOLS)\s*=\s*(\[.*?\]);', page, re.S):
        region, sub = array_region.get(m.group(1), ('', ''))
        try:
            arr = json.loads(m.group(2))
        except ValueError:
            continue
        for o in arr:
            if isinstance(o, dict) and o.get('school_id') is not None and o.get('lat') is not None:
                coords[o['school_id']] = {
                    'lat': o['lat'],
                    'lon': o.get('lon'),
                    'city': o.get('city', ''),
                    'state': o.get('state', ''),
                    'region': region,
                    'sub': sub,
                }
    return coords


def scrape_dates():
    """school_id -> ISO date that school's postings were last scraped."""
    out = {}
    for path in glob.glob(os.path.join(POSTS_CODE_DIR, 'school_id_*_job_postings.checkpoint')):
        try:
            sid = int(os.path.basename(path).split('_')[2])
            with open(path, encoding='utf-8') as f:
                ckpt = json.load(f)
        except (ValueError, OSError):
            continue
        stamp = ckpt.get('completed_at') or ckpt.get('updated_at') or ''
        out[sid] = stamp[:10]
    return out


def main():
    meta = load_school_meta()
    coords = load_coords()
    seen_on = scrape_dates()

    postings = []
    schools_used = {}
    skipped_no_coords = set()
    for path in sorted(glob.glob(os.path.join(INFO_DIR, '*.csv'))):
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    sid = int(row['school_id'])
                except (KeyError, TypeError, ValueError):
                    continue
                title = (row.get('job_title_in_post') or '').strip()
                if not title:
                    continue  # a posting with no readable title isn't searchable
                geo = coords.get(sid)
                if not geo:
                    skipped_no_coords.add(sid)
                    continue
                school = meta.get(sid, {})
                keywords = (row.get('area_key_words') or '').strip()
                dept = (row.get('department_or_school') or '').strip()
                schools_used[sid] = {
                    'name': school.get('name', ''),
                    'country': school.get('country', ''),
                    'city': geo.get('city', ''),
                    'lat': geo['lat'],
                    'lon': geo['lon'],
                    'region': geo.get('region', ''),
                    'sub': geo.get('sub', ''),
                    'seen': seen_on.get(sid, ''),
                }
                # School name/country/coords live once in `schools`, not on
                # every posting: repeating them inline made the file 3.6 MB,
                # which is a slow first paint for a page that also has to
                # load the basemap. The searchable text is likewise built
                # client-side from title+kw+dept rather than shipped.
                postings.append({
                    's': sid,
                    't': title,
                    'p': [t for t in (row.get('position_type') or '').split('; ') if t],
                    'j': (row.get('job_term') or '').strip(),
                    'd': dept,
                    'k': keywords,
                    'u': (row.get('posting_url') or '').strip(),
                    'x': normalize_date(row.get('deadline_of_application')),
                    'b': normalize_date(row.get('position_start_date')),
                })

    payload = {
        'generated': datetime.now().isoformat(timespec='seconds'),
        'scrape_dates': sorted({d for d in seen_on.values() if d}),
        'count': len(postings),
        'schools': schools_used,
        'postings': postings,
    }
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))

    size_mb = os.path.getsize(OUT_PATH) / 1e6
    print(f'wrote {OUT_PATH} -- {len(postings)} postings, {size_mb:.2f} MB')
    if skipped_no_coords:
        print(f'skipped {len(skipped_no_coords)} schools with no coordinates: '
              f'{sorted(skipped_no_coords)[:10]}')
    with_start = sum(1 for p in postings if p['b'])
    with_deadline = sum(1 for p in postings if p['x'])
    asst = sum(1 for p in postings if 'Assistant_Professor' in p['p'])
    print(f'  Assistant Professor postings: {asst}')
    print(f'  with parsed start date: {with_start} ({100 * with_start / max(len(postings), 1):.0f}%)')
    print(f'  with parsed deadline:   {with_deadline} '
          f'({100 * with_deadline / max(len(postings), 1):.0f}%)')


if __name__ == '__main__':
    main()
