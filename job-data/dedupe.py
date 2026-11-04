"""Remove duplicate postings before the map is written (build_map_data.py).

Two kinds of duplicate reached the map (2026-10-16 count: ~2,050 + ~800):

1. ONE posting listed under SEVERAL schools. Campuses of one system that
   share a job board (UW Seattle / Tacoma / Bothell, Oregon State and
   OSU-Cascades, the Penn State campuses, Black Hills State and South
   Dakota, ...) each scraped the whole board, so every job showed once per
   campus. The posting is kept under the campus its own text names (city or
   campus name in the title, department or advert); when the text names
   none of them, under the campus that holds most of the shared postings
   (the board's home campus).

2. The SAME ADVERT posted twice by one school -- same title, same text,
   new requisition number (Auburn's "Assistant Professor ..." twice, UCA's
   "Clinical Instructor I" twice). Only the newest is kept. Openings that
   merely share a generic title ("Postdoctoral Fellow", "Lecturer pool")
   but differ in their text are all kept.

The advert texts come from each school's info checkpoint (raw description),
read only for the schools that have a candidate group.
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INFO_CODE = os.path.join(HERE, 'school_job_info_code')

_NUMBERS = re.compile(r'(?i)\b(?:posting|job|requisition|req|position)\s*(?:number|no\.?|id|#|code)\s*:?\s*\S+')


def _descriptions(sid):
    path = os.path.join(INFO_CODE, f'school_id_{sid}_job_info.checkpoint')
    try:
        with open(path, encoding='utf-8') as f:
            raw = json.load(f).get('raw') or {}
    except (OSError, ValueError):
        return {}
    return {u: (r.get('description') or '') for u, r in raw.items() if isinstance(r, dict)}


def _advert_key(text):
    """The whole advert, numbers stripped. Not a prefix: UMGC's pages open
    with 3,000+ characters of site menus, so a prefix made the same adjunct
    post at different bases look like one."""
    text = _NUMBERS.sub('', text or '')
    return re.sub(r'\s+', ' ', text).strip().lower()


def _campus_words(name, city):
    """Words that identify a campus in an advert: the part of the school
    name after the system name ("University of Washington-Tacoma" ->
    "Tacoma") and the city on the map."""
    words = set()
    if '-' in name:
        words.add(name.rsplit('-', 1)[1].strip())
    m = re.search(r'\bat (.+)$', name)
    if m:
        words.add(m.group(1).strip())
    if city:
        words.add(city.strip())
    # the institution's own name, as boards that serve several schools print
    # it ("Institution: Black Hills State University" on South Dakota's)
    if '-' not in name:
        words.add(re.sub(r'^The ', '', name.strip()))
    return {w for w in words if len(w) >= 4 and not re.fullmatch(r'(?i)main campus|campus|university|college', w)}


def dedupe(postings, meta, coords, first_seen):
    """Return (postings, stats). `postings` carry full URLs in 'u'."""
    stats = {'cross_school': 0, 'reposted': 0}

    # ---- 1. one URL under several schools
    by_url = collections.defaultdict(list)
    for i, p in enumerate(postings):
        if p['u']:
            by_url[p['u']].append(i)
    shared = {u: ix for u, ix in by_url.items() if len({postings[i]['s'] for i in ix}) > 1}
    drop = set()
    if shared:
        hub = collections.Counter()
        for ix in shared.values():
            for i in ix:
                hub[postings[i]['s']] += 1
        texts = {}
        for sid in {postings[i]['s'] for ix in shared.values() for i in ix}:
            texts.update(_descriptions(sid))
        total = collections.Counter(p['s'] for p in postings)
        for url, ix in shared.items():
            p0 = postings[ix[0]]
            fields = (url.replace('-', ' ').replace('_', ' ').replace('/', ' '),   # Workday: /job/Corvallis/...
                      ' '.join((p0['t'], p0.get('d', ''))),
                      texts.get(url, '')[:600])                                 # location sits near the top
            best, best_key = None, None
            for i in ix:
                sid = postings[i]['s']
                name = meta.get(sid, {}).get('name', '')
                words = _campus_words(name, (coords.get(sid) or {}).get('city', ''))
                score = tuple(sum(1 for w in words if re.search(r'\b' + re.escape(w) + r'\b', f, re.I)) for f in fields)
                # No campus named anywhere: the system's main campus -- the
                # higher research class (R1 > R2), a name without a campus
                # suffix or with "Main Campus", the larger programs.
                geo = coords.get(sid) or {}
                home = ('-' not in name) + bool(re.search(r'(?i)main campus', name))
                research = {'R1': 3, 'R2': 2}.get(geo.get('research') or '', 1 if geo.get('research') else 0)
                key = (score, research, home, geo.get('size') or 0, total[sid], -sid)
                if best_key is None or key > best_key:
                    best, best_key = i, key
            for i in ix:
                if i != best:
                    drop.add(i)
        stats['cross_school'] = len(drop)

    # ---- 2. the same advert posted twice by one school
    kept = [p for i, p in enumerate(postings) if i not in drop]
    groups = collections.defaultdict(list)
    for p in kept:
        groups[(p['s'], re.sub(r'\s+', ' ', p['t']).strip().lower())].append(p)
    candidates = {k: v for k, v in groups.items() if len(v) > 1}
    reposted = set()
    for sid in {k[0] for k in candidates}:
        texts = _descriptions(sid)
        for (s, _t), group in candidates.items():
            if s != sid:
                continue
            by_text = collections.defaultdict(list)
            for p in group:
                key = _advert_key(texts.get(p['u'], ''))
                # a short text is page furniture (The New School's banner,
                # 287 characters), not an advert -- it can't prove two
                # postings are the same job
                if len(key) >= 600:
                    by_text[key].append(p)
            for same in by_text.values():
                if len(same) < 2:
                    continue
                newest = max(same, key=lambda q: (first_seen.get(q['u'], ''), q['u']))
                reposted.update(id(q) for q in same if q is not newest)
    stats['reposted'] = len(reposted)
    return [p for p in kept if id(p) not in reposted], stats
