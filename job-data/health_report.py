"""Daily health report: what in today's run needs a human look.

Compares every school with the previous run's snapshot and writes
job-data/health/report.md, which the publish stage pushes and a GitHub
Actions workflow turns into an issue (so GitHub emails it). Problems that
used to surface only when the user noticed a missing job -- Spring Arbor at
0 jobs for days, Seton Hall's blank titles, Whitewater filtered out -- are
what this looks for.

Run from job-data/ after build_map_data.py:
    python3 health_report.py [--log PATH_TO_TODAYS_REFRESH_LOG]
"""
import argparse
import collections
import csv
import glob
import json
import os
import re
import sys
import time
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import onedrive_io  # noqa: F401
import job_info_lib as J
from faculty_filter import is_faculty
from discipline_filter import is_relevant

ROOT = os.path.dirname(HERE)
HEALTH_DIR = os.path.join(HERE, 'health')
SNAPSHOT = os.path.join(HEALTH_DIR, 'snapshot.json')
REPORT = os.path.join(HEALTH_DIR, 'report.md')
RUN_LOG_DIRS = [os.path.expanduser('~/Library/Logs/faculty-job-atlas/run_logs'),
                os.path.join(HERE, 'refresh_logs')]

# Words next to the user's fields. A faculty posting that names one of these
# but was filtered out is listed for a human decision (Whitewater's
# "Information Technology and Supply Chain Management" was one).
NEAR = re.compile(
    r"(?i)analytic|\bdata\b|statistic|quantitative|operations|decision|information\s+technolog|"
    r"informatics|optimi[sz]|econometric|actuarial|management\s+science|supply\s+chain|"
    r"\bAI\b|artificial\s+intelligence|machine\s+learning|applied\s+math|business\s+information|"
    r"computer\s+information|information\s+management")


def load_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def run_statuses(stage):
    """{school_id: (status, error)} from today's run logs; a later file (the
    serial retry pass) overrides the parallel shards."""
    files = []
    for d in RUN_LOG_DIRS:
        files += glob.glob(os.path.join(d, f'run_log_*_{stage}*.csv'))
    cutoff = time.time() - 20 * 3600
    out = {}
    for path in sorted((f for f in files if os.path.getmtime(f) >= cutoff), key=os.path.getmtime):
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                out[r['school_id']] = (r['status'], r.get('error', ''))
    return out


def run_summary(log_path):
    """Stage start times and failures from the refresh log."""
    if not log_path or not os.path.exists(log_path):
        return {}
    text = open(log_path, encoding='utf-8', errors='replace').read()
    start = text.rfind('refresh started')
    text = text[start:] if start >= 0 else text
    stages = re.findall(r'--- (\d)/6 [^(]*\((\d\d:\d\d:\d\d)\)', text)
    return {'stages': stages,
            'failures': re.findall(r'stage failed \(attempt \d\)', text),
            'git': re.findall(r'(COMMIT FAILED[^\n]*|PUSH FAILED[^\n]*)', text)}


def hours_between(a, b):
    t = [datetime.strptime(x, '%H:%M:%S') for x in (a, b)]
    secs = (t[1] - t[0]).total_seconds() % 86400
    return f'{secs / 3600:.1f} h'


def post_issue(body):
    """Open today's report as an issue (labelled health-report) and close
    the previous one. Posted with the git login saved on this machine, not
    via GitHub Actions: the account's Actions were locked over a billing
    issue on 2026-11-09. GitHub emails your own issues only if "Include your
    own updates" is on in Settings > Notifications."""
    import subprocess
    import requests
    cred = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                          capture_output=True, text=True, timeout=30).stdout
    token = next((l.split('=', 1)[1] for l in cred.splitlines() if l.startswith('password=')), '')
    if not token:
        print('no GitHub credential; report not posted')
        return
    api = 'https://api.github.com/repos/yw825/faculty-job-atlas'
    h = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
    first = body.split('\n')[0].lstrip('# ')
    m = re.search(r'\*\*(\d+) items need a look', body)
    title = f"{first}: {m.group(1) + ' items need a look' if m else 'all clear'}"
    for issue in requests.get(f'{api}/issues', headers=h, timeout=30,
                              params={'labels': 'health-report', 'state': 'open'}).json():
        requests.patch(f"{api}/issues/{issue['number']}", headers=h, json={'state': 'closed'}, timeout=30)
    r = requests.post(f'{api}/issues', headers=h, timeout=30,
                      json={'title': title, 'body': body[:60000], 'labels': ['health-report']})
    print('posted' if r.status_code == 201 else f'posting failed: {r.status_code} {r.text[:200]}',
          r.json().get('html_url', '') if r.ok else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', default='')
    ap.add_argument('--post', action='store_true', help='post the report as a GitHub issue')
    args = ap.parse_args()

    names = {r['school_id']: r['name'] for r in csv.DictReader(
        open(os.path.join(HERE, 'schools_master.csv'), encoding='utf-8'))}
    prev = load_json(SNAPSHOT, {})
    prev_schools = prev.get('schools', {})
    prev_near = set(prev.get('near_seen', []))
    first_run = not prev

    payload = load_json(os.path.join(ROOT, 'postings.json'), {'postings': []})
    on_map = collections.Counter(str(p.get('s')) for p in payload['postings'])
    post_runs, info_runs = run_statuses('postings'), run_statuses('info')

    schools, near_now, near_new = {}, set(), []
    for sid, name in names.items():
        pck = J.load_checkpoint(os.path.join(HERE, 'school_job_posts_code',
                                             f'school_id_{sid}_job_postings.checkpoint'))
        ick = J.load_checkpoint(os.path.join(HERE, 'school_job_info_code',
                                             f'school_id_{sid}_job_info.checkpoint'))
        links = pck.get('links', [])
        raw = ick.get('raw', {})
        unread = sum(1 for u in links if J._needs_fetch(raw.get(u)))
        rows = []
        path = os.path.join(HERE, 'school_job_info', f'school_id_{sid}_job_info.csv')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
        titles = [(r.get('job_title_in_post') or '').strip() for r in rows]
        blank = sum(1 for t in titles if not t)
        chrome = sum(1 for t in titles if t and J._CHROME_TITLE_RE.match(t.rstrip(' .')))
        top_title, top_n = (collections.Counter(t for t in titles if t).most_common(1) or [('', 0)])[0]
        p_status, p_err = post_runs.get(sid, (pck.get('status', ''), pck.get('last_error', '')))
        if p_status != 'complete':
            p_err = p_err or pck.get('last_error', '')
        p_err = re.sub(r'\s+', ' ', (p_err or '').split('Call log')[0]).strip()
        old = prev_schools.get(sid, {})
        failed = p_status in ('error', 'timeout')
        err_days = old.get('err_days', 0) + 1 if failed else 0
        warn = pck.get('last_warning', '')
        schools[sid] = {
            'links': len(links), 'map': on_map.get(sid, 0), 'unread': unread,
            'rows': len(rows), 'blank': blank, 'chrome': chrome,
            'top_title': top_title[:80], 'top_n': top_n,
            'p_status': p_status, 'p_err': (p_err or '')[:160], 'err_days': err_days,
            'i_status': info_runs.get(sid, ('', ''))[0],
            'i_err': re.sub(r'\s+', ' ', (info_runs.get(sid, ('', ''))[1] or '').split('Call log')[0])[:160],
            'warn': warn[:200] if warn[:10] == date.today().isoformat() else '',
        }
        for r in rows:
            t = (r.get('job_title_in_post') or '').strip()
            dept = (r.get('department_or_school') or '').strip()
            if not t or not NEAR.search(t + ' ' + dept):
                continue
            if not is_faculty(t, (r.get('position_type') or '').split('; '), int(sid)):
                continue
            if is_relevant(t, dept, (r.get('area_key_words') or '').strip()):
                continue
            url = r.get('posting_url') or ''
            near_now.add(url)
            if url not in prev_near:
                near_new.append((name, t, dept))

    # ---- what needs a look ----
    sections, n_items = [], [0]

    def section(title, lines, note=''):
        n_items[0] += len(lines)
        if lines:
            sections.append(f'### {title} ({len(lines)})\n' + (f'_{note}_\n\n' if note else '\n')
                            + '\n'.join(f'- {x}' for x in lines))

    def label(sid):
        return f'**{names[sid]}** ({sid})'

    zero, drops, map_zero, errs, guard, unread, junk, info_err, once = [], [], [], [], [], [], [], [], []
    for sid, s in schools.items():
        o = prev_schools.get(sid)
        if o:
            if s['links'] == 0 and o['links'] >= 3:
                zero.append(f"{label(sid)}: {o['links']} → 0 links")
            elif o['links'] >= 10 and s['links'] < 0.6 * o['links']:
                drops.append(f"{label(sid)}: {o['links']} → {s['links']} links")
            if o.get('map', 0) >= 2 and s['map'] == 0:
                map_zero.append(f"{label(sid)}: {o['map']} → 0 jobs on the map")
        if s['err_days'] >= 2:
            errs.append(f"{label(sid)}: {s['err_days']} runs in a row — {s['p_err'][:110]}")
        elif s['err_days'] == 1:
            once.append(names[sid])
        if s['warn']:
            guard.append(f"{label(sid)}: {s['warn'][27:150]}")
        if s['unread'] >= 5 and s['unread'] >= 0.2 * max(s['links'], 1):
            unread.append(f"{label(sid)}: {s['unread']} of {s['links']} jobs have no details")
        if s['i_status'] in ('error', 'timeout'):
            info_err.append(f"{label(sid)}: {s['i_status']} — {s['i_err'][:110]}")
        bad_titles = s['blank'] + s['chrome']
        if bad_titles >= 3:
            junk.append(f"{label(sid)}: {s['blank']} blank, {s['chrome']} page-heading titles of {s['rows']}")
        elif s['top_n'] >= 5 and s['top_n'] >= 0.5 * s['rows'] and not re.search(
                r'(?i)adjunct|lecturer|instructor|faculty|professor|pool', s['top_title']):
            junk.append(f"{label(sid)}: {s['top_n']} of {s['rows']} jobs titled “{s['top_title']}”")

    section('Link finder now finds nothing', zero, 'Likely a board change (Spring Arbor, Nov 2026).')
    section('Jobs on the map dropped to zero', map_zero)
    section('Big drop in links', drops, 'Could be closings; worth a glance if it looks too big.')
    section('Link finder keeps failing', errs,
            'Links from the last good run are kept, but new jobs are missed until this is fixed.')
    section('Shrink guard held the old links', guard, 'The board returned far fewer links than before.')
    section('Detail reader failed', info_err)
    section('Jobs without details', unread)
    section('Suspicious titles', junk, 'Blank titles or site headings instead of job titles.')

    near_lines = [f"{t} — {n}" + (f" ({d})" if d else '') for n, t, d in sorted(near_new)[:40]]
    if first_run:
        near_note = f'{len(near_now)} faculty jobs mention a nearby field but are filtered out (baseline; only new ones are listed from now on).'
    else:
        section('Possibly in your fields but filtered out — new since last run', near_lines,
                'Faculty jobs mentioning a nearby field (analytics, data, IT, operations…). '
                'Reply with any that should be on the map.')
        near_note = ''

    # ---- run summary ----
    run = run_summary(args.log)
    st = dict((n, t) for n, t in run.get('stages', []))
    run_bits = []
    if '1' in st and '2' in st:
        run_bits.append(f"finding links {hours_between(st['1'], st['2'])}")
    if '3' in st and '4' in st:
        run_bits.append(f"reading details {hours_between(st['3'], st['4'])}")
    map_now = len(payload['postings'])
    map_prev = prev.get('map_total')
    delta = f" ({map_now - map_prev:+d} vs last run)" if map_prev is not None else ''
    today = date.today().isoformat()
    head = [f'# Health report {today}', '',
            f"**Map:** {map_now} jobs{delta}, {payload.get('first_seen_new', 0)} new today.",
            f"**Run:** {', '.join(run_bits) or 'timing not available'}."]
    if run.get('failures'):
        head.append(f"**Stages retried:** {len(run['failures'])} (OneDrive or crash; see the log).")
    if run.get('git'):
        head.append('**Publish problem:** ' + '; '.join(run['git']))
    head.append('')
    head.append(f'**{n_items[0]} items need a look.**' if n_items[0] else '**Nothing needs a look today.**')
    if once:
        head.append(f"\n_Failed once today (usually a slow site; listed above if it repeats): {', '.join(sorted(once))}._")
    if near_note:
        head.append(f'\n_{near_note}_')
    body = '\n'.join(head) + ('\n\n' + '\n\n'.join(sections) if sections else '') + '\n'

    os.makedirs(HEALTH_DIR, exist_ok=True)
    onedrive_io.write_text(REPORT, body)
    onedrive_io.write_text(SNAPSHOT, json.dumps({
        'date': today, 'map_total': map_now, 'schools': schools,
        'near_seen': sorted(near_now | prev_near)}, ensure_ascii=False))
    print(body)
    if args.post:
        post_issue(body)


if __name__ == '__main__':
    main()
