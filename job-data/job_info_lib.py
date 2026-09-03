"""
Shared engine behind every school_id_<id>_job_info.py script in
school_job_info_code/. Reuses only the low-level fetch/browser/checkpoint
primitives from job_postings_lib.py (my own code from this session) -- no
dependency on scrape_job_postings.py.

Input: the posting URLs already found by that school's job_postings run --
read directly from its checkpoint (school_job_posts_code/school_id_<id>_
job_postings.checkpoint's `links` field), not a separate copy, so job_info
always processes whatever job_postings currently knows about. Re-running
job_postings and finding new links means the next job_info run picks up
exactly those new links; nothing already processed is re-fetched.

Output: school_job_info/school_id_<id>_job_info.csv -- one row per posting:
school_id, posting_url, job_title_in_post, position_type, job_term,
department_or_school, area_key_words, deadline_of_application,
position_start_date.

Checkpoint: school_id_<id>_job_info.checkpoint (JSON) next to the
per-school script. `rows` maps posting URL -> its extracted row, built up
one posting at a time and saved after each one -- kill-and-resume at
per-posting granularity: a run picks up exactly where a previous one
stopped, never re-fetching a posting already recorded in `rows`.

Two kinds of school, matching job_postings' split:
  - A school on a platform with a BULK_ADAPTER (currently just Oracle Cloud
    HCM) gets every posting's title/department/description/deadline back
    from ONE listing API call -- confirmed on Birmingham: the same call
    scrape_oracle already uses for links also carries these fields, so
    fetching each of 33 posting pages individually would have been pure
    waste. Reused as real platform-wide code, same reasoning as
    job_postings_lib's PLATFORM_ADAPTERS.
  - Every other school visits each posting URL individually via
    fetch_detail_fn (default: render the page, take the first heading as
    the title and the rest of the visible text as the description) --
    each per-school script can override fetch_detail_fn with its own logic
    exactly like job_postings' find_links(), since a posting page's layout
    is as school-specific as its listing page was.

classify_row() (position_type / job_term / department_or_school /
deadline_of_application / position_start_date) is ENGLISH-LANGUAGE, RULE-
BASED text matching -- not a human reading each posting the way Birmingham's
original school_id_1763_job_info.csv was hand-built. It will not match that
by-hand quality, especially area_key_words (a real summarization judgment
call, approximated here as the most distinctive noun-ish phrases pulled
from the title/description, not a semantic understanding of the role) and
department_or_school on schools whose postings don't literally contain a
"Department of X" / "School of X" style clause. Test against Birmingham's
existing hand file before trusting this on schools without a ground truth
to check against.
"""
import csv
import json
import math
import os
import re
from urllib.parse import urlparse

import job_postings_lib as jlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'school_job_info')
POSTS_CODE_DIR = os.path.join(HERE, 'school_job_posts_code')

FIELDS = ['school_id', 'posting_url', 'job_title_in_post', 'position_type', 'job_term',
          'department_or_school', 'area_key_words', 'deadline_of_application',
          'position_start_date']

# Re-exported so a per-school script can do `from job_info_lib import fetch_rendered`
# without a second import line.
fetch_static = jlib.fetch_static
fetch_rendered = jlib.fetch_rendered
is_fetch_failure = jlib.is_fetch_failure
get_browser = jlib.get_browser
close_browser = jlib.close_browser
now_iso = jlib.now_iso


# --------------------------------------------------------------------------
# Checkpoint I/O
# --------------------------------------------------------------------------

def load_checkpoint(path):
    return jlib.load_checkpoint(path)


def save_checkpoint(path, data):
    jlib.save_checkpoint(path, data)


def load_posting_links(job_postings_checkpoint_path):
    """The list of posting URLs this school's job_postings run has found so
    far -- read live from ITS checkpoint, so job_info always tracks
    whatever job_postings currently knows, not a stale copy."""
    ckpt = jlib.load_checkpoint(job_postings_checkpoint_path)
    return list(ckpt.get('links', []))


def write_info_csv(school_id, rows_by_url, ordered_urls):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f'school_id_{school_id}_job_info.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for url in ordered_urls:
            row = rows_by_url.get(url)
            if row and 'error' not in row:
                w.writerow(row)
    return path


# --------------------------------------------------------------------------
# Text classification -- English-language, rule-based. See module docstring
# for the honesty caveat on area_key_words and department_or_school.
# --------------------------------------------------------------------------

POSITION_TYPE_VALUES = ('Assistant_Professor', 'Associate_Professor', 'Full_Professor',
                         'Lecturer', 'Research_Fellow', 'Non-academic')

_BOTH_AP_RE = re.compile(r'assistant\s*(?:/|,|\bor\b)\s*associate\s+professor', re.I)
_ASSISTANT_PROF_RE = re.compile(r'\bassistant\s+professor\b', re.I)
_ASSOCIATE_PROF_RE = re.compile(r'\bassociate\s+professor\b', re.I)
_PROFESSOR_RE = re.compile(r'\bprofessor\b', re.I)
_LECTURER_RE = re.compile(r'\b(teaching fellow|senior lecturer|lecturer)\b', re.I)
_RESEARCH_FELLOW_RE = re.compile(
    r'\b(research fellow|research associate|research scientist|'
    r'post[- ]?doc(?:toral)?(?:\s+research(?:er)?)?|postdoctoral researcher)\b', re.I)
_NON_ACADEMIC_RE = re.compile(
    r'\b(technician|research assistant\b(?!\s+professor)|support officer|administrator|'
    r'coordinator|manager|analyst|specialist|librarian|clerk)\b', re.I)


def classify_position_type(title, description=''):
    """Returns a list of POSITION_TYPE_VALUES entries (possibly more than
    one, e.g. a posting spanning "Assistant or Associate Professor"), or
    ['Unclassified'] if nothing matched."""
    text = f'{title} {description}'
    values = []
    if _BOTH_AP_RE.search(text):
        values += ['Assistant_Professor', 'Associate_Professor']
    else:
        if _ASSISTANT_PROF_RE.search(text):
            values.append('Assistant_Professor')
        if _ASSOCIATE_PROF_RE.search(text):
            values.append('Associate_Professor')
        if not values and _PROFESSOR_RE.search(text):
            values.append('Full_Professor')
    if _LECTURER_RE.search(text):
        values.append('Lecturer')
    if _RESEARCH_FELLOW_RE.search(text):
        values.append('Research_Fellow')
    if not values and _NON_ACADEMIC_RE.search(text):
        values.append('Non-academic')
    seen, out = set(), []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out or ['Unclassified']


_PART_TIME_RE = re.compile(r'\b(part[- ]time|fractional|0\.\d+\s*fte|\d+%\s*fte)\b', re.I)


def classify_job_term(title, description=''):
    return 'Part-time' if _PART_TIME_RE.search(f'{title} {description}') else 'Full-time'


_DEPT_RE = re.compile(
    r'\b((?:Department|Dept\.?|School|College|Faculty|Institute|Division|Centre|Center)\s+'
    # A real department name can itself contain a comma ("School of Sport,
    # Exercise and Rehabilitation Sciences" -- confirmed live on Birmingham
    # posting 9791, where stopping at the comma truncated it) -- so only a
    # dash-separated clause boundary, sentence end, or newline ends the
    # match, never a bare comma.
    r'(?:of|for)\s+[A-Z][A-Za-z&,\'\s]{2,80}?)(?=\.\s|\.$|\n|$| - |\s+-\s+)', re.I)


def extract_department(title, description=''):
    m = _DEPT_RE.search(title) or _DEPT_RE.search(description)
    return m.group(1).strip() if m else ''


_MONTH_NAMES = (r'january|february|march|april|may|june|july|august|'
                r'september|october|november|december')
_ISO_DATE_RE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
_SLASH_DATE_RE = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b')
_MONTH_DATE_RE = re.compile(
    # The year is captured as 4 digits with an OPTIONAL single space before
    # each one (\d(?:\s?\d){3}), not a plain \d{4} -- pypdf's text
    # extraction occasionally renders a year with a stray space stuck
    # inside it (confirmed on real University of New Brunswick PDFs: "July
    # 1, 202 6" and "August 1, 202 5" -- a kerning/font quirk in the
    # source, split at a different digit each time, not a fixed 2+2
    # pattern). Month/day/year are named groups specifically so cleanup can
    # rebuild a normalized date from just the year's digits, rather than
    # blindly collapsing every digit-space-digit pair in the match (which
    # would wrongly fuse an unrelated day+year pair like "1 2026" with no
    # comma into "12026").
    rf'\b(?P<month>{_MONTH_NAMES})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?,?\s+'
    rf'(?P<year>\d(?:\s?\d){{3}})\b', re.I)


def _clean_date_match(m):
    if m.re is _MONTH_DATE_RE:
        month = m.group('month').capitalize()
        day = m.group('day')
        year = re.sub(r'\s', '', m.group('year'))
        return f'{month} {day}, {year}'
    return re.sub(r'\s+', ' ', m.group(0)).strip().rstrip('.,;')


def _find_date_near(text, include_signals, exclude_signals, window=70):
    """Finds every date-shaped match (ISO, slash, or Month-name) in `text`,
    keeps the ones preceded -- within `window` characters -- by at least
    one of `include_signals` and NONE of `exclude_signals`, and returns the
    earliest such match (cleaned), or ''.

    The exclude list is doing as much work as the include list. The same
    real postings that say "the position will begin July 1, 2026" also say
    "Review of applications will begin October 6, 2025" (confirmed live on
    UNB's psychology posting) -- both use "begin" right next to a date, so
    matching on "begin" alone would grab the wrong one for a start date (or
    the wrong one for a deadline). Checking that the *other* signal's words
    are absent from the same window is what actually tells them apart."""
    candidates = []
    for pattern in (_ISO_DATE_RE, _MONTH_DATE_RE, _SLASH_DATE_RE):
        for m in pattern.finditer(text):
            window_text = text[max(0, m.start() - window):m.start()]
            if (any(re.search(sig, window_text, re.I) for sig in include_signals) and
                    not any(re.search(sig, window_text, re.I) for sig in exclude_signals)):
                candidates.append((m.start(), _clean_date_match(m)))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1] if candidates else ''


_START_INCLUDE = (r'\bstart\b', r'\bbegin\b', r'\bcommenc\w*', r'\beffective\b', r'\bas of\b')
_START_EXCLUDE = (r'\bapplication', r'\breview\b', r'\bclos\w*', r'\bdeadline\b')

_DEADLINE_INCLUDE = (r'\bclos\w*', r'\bdeadline\b', r'\bapply\b', r'\bapplications?\b',
                      r'\breview of applications')
_DEADLINE_EXCLUDE = (r'\bstart\b', r'\bcommenc\w*', r'\bposition (?:will |is )', r'\bappointment\b')


def extract_start_date(description=''):
    return _find_date_near(description or '', _START_INCLUDE, _START_EXCLUDE)


def extract_deadline(description=''):
    return _find_date_near(description or '', _DEADLINE_INCLUDE, _DEADLINE_EXCLUDE)



# --------------------------------------------------------------------------
# area_key_words: two parts, per explicit user instruction --
#   1. A rule-based PRIMARY keyword read straight off the position in the
#      title, when the title states one -- e.g. "Assistant Professor in
#      Business Analytics" -> "Business Analytics". No LLM call, no
#      ambiguity: it's literally there in the rank clause.
#   2. 2-3 SUPPORTING keywords for what courses it wants taught / what
#      research area it wants pursued. The user's preferred way to get
#      these is an LLM read of the description (llm_extract_keywords,
#      below) -- but this session has no ANTHROPIC_API_KEY and the user
#      confirmed they don't have one either ("I don't have API, so do
#      whatever you can do best"), so the DEFAULT path is corpus-relative
#      TF-IDF instead: score each candidate phrase in a posting's
#      description by how rare it is ACROSS THIS SCHOOL'S OTHER POSTINGS,
#      not just its raw frequency. Plain word-frequency was tried first and
#      was mostly noise (confirmed on Birmingham: "research; contribute;
#      delivery" instead of "nanomaterials; mitochondrial nucleic acid
#      delivery") because Oracle's shared description boilerplate ("please
#      note", "we welcome applications", "closes", "contribute to...")
#      repeats near-identically across EVERY posting from the same school
#      -- TF-IDF suppresses exactly that shared boilerplate automatically,
#      without a hand-maintained stopword list having to name it, because a
#      phrase that appears in most of a school's postings is by definition
#      not distinctive to any one of them. llm_extract_keywords is left in
#      place, unused by default, for whoever later has API access to
#      switch on via use_llm=True.
# --------------------------------------------------------------------------

_RANK_SUBJECT_RE = re.compile(
    r'\b(?:in|of)\s+([A-Z][A-Za-z0-9&,\'\s]{2,60}?)(?=\s*\(|$)')


def extract_primary_keyword(title):
    """The subject named directly in the rank clause of the title, e.g.
    "Assistant Professor in Business Analytics" -> "Business Analytics",
    "Professor of Statistics" -> "Statistics". Only looks at the text
    before the first genuine clause-dash (a dash preceded by whitespace --
    Oracle-style titles append " - Department of X - <req id> - Grade N"
    after the role, and a hyphen with NO preceding space, like
    "BCC-Superalloys", is part of a compound word, not a clause break).
    Returns '' if the title states no explicit subject this way (many
    postings don't, e.g. "Research Fellow - Department of Pharmacy - ...")."""
    role_clause = re.split(r'\s-\s*', title, maxsplit=1)[0]
    m = _RANK_SUBJECT_RE.search(role_clause)
    return m.group(1).strip() if m else ''


LLM_KEYWORD_MODEL = 'claude-opus-5'

_KEYWORD_PROMPT = """Read this academic job posting and name 2-3 SHORT keyword phrases for the specific courses it wants taught and/or the specific research area/topic it wants pursued -- not generic words like "research", "teaching", "faculty", "university". If a primary subject is already given below, don't repeat it; give the more specific sub-topics instead.

Title: {title}
{primary_line}
Description:
{description}

Respond with ONLY a comma-separated list of 2-3 short keyword phrases. No numbering, no explanation, no other text."""


def llm_extract_keywords(title, description, primary_keyword='', client=None):
    """One Claude API call per posting -- see job_info_lib module docstring
    and the per-school script's own docstring for the cost/scale tradeoff
    this implies at the full 302-school scale (thousands of postings).
    Requires ANTHROPIC_API_KEY (or an `ant auth login` profile) in the
    environment the script actually runs in -- NOT available in the
    session this code was written in, so this function could not be
    validated live there; test it yourself with real credentials before
    trusting it at scale."""
    import anthropic
    client = client or anthropic.Anthropic()
    primary_line = f'Primary subject already identified: {primary_keyword}' if primary_keyword else ''
    prompt = _KEYWORD_PROMPT.format(title=title, primary_line=primary_line,
                                     description=(description or '')[:4000])
    response = client.messages.create(
        model=LLM_KEYWORD_MODEL,
        max_tokens=150,
        output_config={'effort': 'low'},
        messages=[{'role': 'user', 'content': prompt}],
    )
    text = ''.join(b.text for b in response.content if b.type == 'text').strip()
    parts = [p.strip() for p in text.split(',') if p.strip()]
    return parts[:3]


# Boilerplate that appears in nearly every academic job posting regardless
# of subject -- not exhaustive on its own (TF-IDF's corpus-relative scoring
# is what actually suppresses shared-template phrases; this list only
# blocks the most universal filler words so they never even become
# candidate phrases in the first place).
_PHRASE_STOPWORDS = set((
    'the a an and or of for to in on at with is are was were be been being will would should '
    'shall must can could may might this that these those as who whom which what when where '
    'why how not no nor but if then than so such very more most other another each every all '
    'any some both either neither own same too also just only even still yet already '
    'you your yours we our ours they their theirs it its he she his her him '
    'applicants applicant candidates candidate applications application apply applying applied '
    'role roles position positions post posts posting postings job jobs vacancy vacancies '
    'department departments school schools university universities college colleges faculty '
    'faculties institute institutes centre centres center centers division divisions '
    'full time part fte hours hour week weeks month months year years annum salary salaries '
    'grade grades required requirement requirements essential desirable criteria '
    'successful appointment appointed appoint interview interviews closing close closes closed '
    'date dates deadline please note contact email further details information please '
    'staff member members team teams work working works opportunity opportunities '
    'contribute contributing contribution activities activity within across include including '
    'ensure ensuring provide providing support supporting supported based responsible '
    'requires require experience skills ability able knowledge understanding demonstrate '
    'excellent strong good high level levels new current existing').split())

_PHRASE_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']+")


def _extract_candidate_phrases(text, max_n=3):
    """Splits text into runs of consecutive non-stopword tokens (a run
    breaks at any stopword or punctuation boundary), then emits every
    contiguous sub-run of length 1..max_n words as a candidate phrase --
    e.g. "gravitational wave astrophysics research" (after "research" is
    filtered as a stopword) yields "gravitational", "wave", "astrophysics",
    "gravitational wave", "wave astrophysics", "gravitational wave
    astrophysics". Returns a phrase -> count-in-this-text dict."""
    counts = {}
    for sentence_piece in re.split(r'[.;:\n]', text or ''):
        tokens = _PHRASE_TOKEN_RE.findall(sentence_piece)
        run = []
        for tok in tokens + ['']:  # sentinel flushes the final run
            lw = tok.lower()
            if tok and lw not in _PHRASE_STOPWORDS and len(tok) >= 3:
                run.append(tok)
                continue
            for n in range(1, max_n + 1):
                for i in range(0, len(run) - n + 1):
                    phrase = ' '.join(run[i:i + n]).lower()
                    counts[phrase] = counts.get(phrase, 0) + 1
            run = []
    return counts


def _posting_text_for_phrases(title, description):
    """Title words go in TWICE -- a subject named only in the title (e.g.
    "Research Fellow (BCC-Superalloys)" never repeating "superalloys" in
    the body text -- confirmed missing live on Birmingham posting 9913
    before this fix) needs a real chance to outscore body-text boilerplate,
    and doubling its term frequency is a simple way to weight it higher
    without a separate scoring path."""
    return f'{title} {title} {description}'


def build_corpus_stats(items):
    """items: an iterable of (title, description) pairs, one per posting,
    for ALL of a school's postings in this run -- document frequency is
    relative to THIS school's own postings, not some external corpus,
    which is exactly what makes it catch that school's own repeated
    boilerplate regardless of what phrasing convention it uses."""
    n_docs = 0
    doc_freq = {}
    for title, desc in items:
        n_docs += 1
        for phrase in _extract_candidate_phrases(_posting_text_for_phrases(title, desc)).keys():
            doc_freq[phrase] = doc_freq.get(phrase, 0) + 1
    return {'n_docs': n_docs, 'doc_freq': doc_freq}


def tfidf_keywords(title, description, corpus_stats, exclude=None, max_keywords=3):
    """Ranks this posting's candidate phrases by tf * log((N+1)/(df+1)) --
    a phrase every posting shares (df ~= N) scores near zero no matter how
    often it repeats within one posting; a phrase unique to this posting
    (df=1) scores highest. Drops single-word phrases that are already
    covered by a kept multi-word phrase (e.g. "waves" once "gravitational
    waves" is kept) and anything matching `exclude` (the title's own
    primary keyword, case-insensitively, so it isn't repeated).

    NOTE this is corpus-relative, not semantic -- it will still suppress a
    genuinely correct topic word if several of a school's OTHER postings
    also happen to use it (confirmed live: Birmingham's several Immunology
    postings all lost "immunology" itself from area_key_words, because it
    wasn't distinctive WITHIN that department cluster even though it's
    exactly the right word). department_or_school already carries that
    signal separately, so the loss is softened but not eliminated -- an
    honest limitation of a non-semantic approach, not a bug to chase
    further with more regex."""
    if not corpus_stats or corpus_stats.get('n_docs', 0) < 2:
        return []
    exclude_lower = (exclude or '').lower()
    n = corpus_stats['n_docs']
    doc_freq = corpus_stats['doc_freq']
    tf = _extract_candidate_phrases(_posting_text_for_phrases(title, description))
    scored = []
    for phrase, count in tf.items():
        if len(phrase) < 4 or phrase == exclude_lower:
            continue
        df = doc_freq.get(phrase, 1)
        score = count * math.log((n + 1) / (df + 1))
        scored.append((score, phrase))
    scored.sort(key=lambda x: (-x[0], -len(x[1]), x[1]))
    out, covered = [], set()
    for score, phrase in scored:
        if score <= 0:
            continue
        if any(phrase in longer or longer in phrase for longer in covered):
            continue
        covered.add(phrase)
        out.append(phrase)
        if len(out) >= max_keywords:
            break
    return out


def extract_keywords(title, description='', corpus_stats=None, use_llm=False, llm_client=None):
    """Primary keyword (rule-based, from the title) + up to 3 supporting
    keywords. Supporting keywords come from llm_extract_keywords when
    use_llm=True (needs API credentials -- opt in once you have them), else
    from tfidf_keywords against corpus_stats (see build_corpus_stats) when
    corpus_stats is given, else there are no supporting keywords and only
    the primary keyword (if the title has one) is returned."""
    primary = extract_primary_keyword(title)
    supporting = []
    if use_llm:
        try:
            supporting = llm_extract_keywords(title, description, primary, client=llm_client)
        except Exception:
            supporting = []
    elif corpus_stats:
        supporting = tfidf_keywords(title, description, corpus_stats, exclude=primary)
    keywords = ([primary] if primary else []) + [s for s in supporting if s.lower() != primary.lower()]
    return '; '.join(keywords)


def classify_row(school_id, url, title, description='', department=None,
                  corpus_stats=None, use_llm=False, llm_client=None):
    """`department`: pass the platform's own structured department field
    when one is available (e.g. Oracle's API returns it directly) instead
    of leaving it to extract_department's regex guess -- confirmed more
    accurate live: Oracle's own field correctly returns names like
    "Birmingham Business School" that don't fit the "Department/School of
    X" pattern extract_department looks for.
    `corpus_stats`/`use_llm`/`llm_client`: see extract_keywords."""
    return {
        'school_id': school_id,
        'posting_url': url,
        'job_title_in_post': title.strip(),
        'position_type': '; '.join(classify_position_type(title, description)),
        'job_term': classify_job_term(title, description),
        'department_or_school': department.strip() if department else extract_department(title, description),
        'area_key_words': extract_keywords(title, description, corpus_stats=corpus_stats,
                                            use_llm=use_llm, llm_client=llm_client),
        'deadline_of_application': extract_deadline(description),
        'position_start_date': extract_start_date(description),
    }


# --------------------------------------------------------------------------
# Generic per-posting-page fetch (default for any school without a bulk
# adapter). A per-school script can pass its own fetch_detail_fn to
# run_school_job_info instead -- own it exactly the way find_links() is
# owned in that school's job_postings script.
# --------------------------------------------------------------------------

# A plain "take the first heading" title picker fails in both directions --
# confirmed live on University of New Brunswick: a careerbeacon.com detail
# page's own <h1> is the EMPLOYER'S name ("University of New Brunswick
# (Academic)"), not the job title at all (the real title -- "Term Assistant
# Professor" -- sits in <title> instead, formatted "Dept: Title at Employer
# | Site"); a PDF posting's first non-blank line is a generic
# "EMPLOYMENT OPPORTUNITIES" header, with the real title several lines down
# ("ASSISTANT OR ASSOCIATE PROFESSOR IN CLINICAL PSYCHOLOGY"). Neither
# "prefer h1" nor "prefer the first line" is a safe universal rule -- what's
# reliable across both is that a real posting TITLE reads like one (names a
# rank), so candidates are ranked by matching that shape instead of by
# their position in the document.
_TITLE_LOOKS_LIKE_JOB_RE = re.compile(
    r'\b(professor|lecturer|fellow|instructor|postdoc|post-doctoral|researcher|'
    r'research associate|teaching|technician|scientist|specialist|coordinator|'
    r'assistant|associate|chair|director|position|tenure)\b', re.I)


def _title_candidates_from_text(raw):
    """Most-trimmed-first: a raw string like "Dept: Title at Employer |
    Site" yields, in order, "Dept: Title at Employer", "Dept: Title", then
    the untrimmed original -- so a caller trying candidates in order finds
    the tightest job-shaped match before falling back to noisier ones."""
    candidates = [raw]
    cur = raw
    for sep in (' | ', ' - '):
        if sep in cur:
            cur = cur.split(sep)[0].strip()
            candidates.insert(0, cur)
    if ' at ' in cur:
        candidates.insert(0, cur.split(' at ')[0].strip())
    return candidates


def _looks_like_heading(text):
    """A real heading/title line is short and doesn't read as a full
    sentence -- distinguishes a genuine header ("TENURE-TRACK POSITION IN
    SUPPLY CHAIN MANAGEMENT AND LOGISTICS") from a body sentence that
    merely happens to mention a rank word in passing ("...at the rank of
    Assistant or Associate Professor. The position is available to start
    on..." -- confirmed live, this wrongly won under a first-job-shaped-
    match-wins rule, since the true header line doesn't contain any of the
    rank words on its own)."""
    return len(text) <= 100 and '. ' not in text.rstrip('.')


def _pick_best_title(candidates):
    """Prefers a candidate that BOTH looks job-shaped (names a rank/the
    word "position") AND looks like a heading rather than a sentence;
    falls back to job-shaped-but-sentence-like, then to the first
    non-empty candidate at all."""
    job_shaped = [c for c in candidates if c and _TITLE_LOOKS_LIKE_JOB_RE.search(c)]
    heading_shaped = [c for c in job_shaped if _looks_like_heading(c)]
    if heading_shaped:
        return heading_shaped[0]
    if job_shaped:
        return job_shaped[0]
    return next((c for c in candidates if c), '')


def fetch_detail_pdf(url):
    """Some schools post the actual opening as a PDF document, not a web
    page (confirmed live: University of New Brunswick links straight to
    PDFs like .../24-09-psychology.pdf). Playwright's page.goto() treats a
    direct PDF URL as a file download rather than a renderable page --
    every one of these failed with "Download is starting" before this was
    added -- so PDFs are downloaded as bytes via plain requests and read
    with pypdf instead of going through the browser at all."""
    import io
    from pypdf import PdfReader
    # Raw bytes, not jlib.fetch_static -- that decodes the response as text,
    # which would garble binary PDF content.
    r = jlib.requests.get(url, headers={'User-Agent': jlib.UA}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f'pdf fetch failed status={r.status_code}')
    reader = PdfReader(io.BytesIO(r.content))
    text = '\n'.join((page.extract_text() or '') for page in reader.pages)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = _pick_best_title(lines[:20])
    return title, text


def fetch_detail_generic(url):
    """Renders the posting page and picks the best-looking title out of
    <h1> and <title> (see _pick_best_title); the description is the page's
    full visible text. Works reasonably across most platforms' own detail
    pages; override per school if a site's detail page needs a click/wait
    first (mirrors job_postings' per-school find_links override)."""
    if url.lower().split('?')[0].endswith('.pdf'):
        return fetch_detail_pdf(url)
    html = jlib.fetch_rendered(url)
    if jlib.is_fetch_failure(html):
        raise RuntimeError(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    candidates = []
    h1 = soup.find('h1')
    if h1:
        candidates += _title_candidates_from_text(h1.get_text(strip=True))
    title_tag = soup.find('title')
    if title_tag:
        candidates += _title_candidates_from_text(title_tag.get_text(strip=True))
    title = _pick_best_title(candidates)
    description = soup.get_text(' ', strip=True)
    return title, description


# --------------------------------------------------------------------------
# Oracle Cloud HCM bulk adapter -- one listing API call already carries
# title/department/description/deadline for every posting (confirmed on
# Birmingham: the same call job_postings_lib.scrape_oracle uses for links).
# --------------------------------------------------------------------------

def fetch_oracle_bulk(careers_link):
    """Returns {posting_url: (title, description, department)} for every posting,
    fetched in one paginated API loop -- not a per-posting page visit."""
    import time as _time
    from urllib.parse import urljoin

    parsed = urlparse(careers_link)
    m = re.search(r'/sites/([^/]+)', parsed.path)
    site_number = m.group(1) if m else None
    base = f'https://{parsed.netloc}'

    b = jlib.get_browser()
    if b is None:
        raise RuntimeError('playwright unavailable')
    captured = {}
    last_err = None
    for _attempt in range(2):
        captured = {}
        page = None
        try:
            page = b.new_page(user_agent=jlib.UA)

            def on_request(req):
                if 'recruitingCEJobRequisitions' in req.url and not captured:
                    captured['headers'] = dict(req.headers)
                    captured['url'] = req.url

            page.on('request', on_request)
            with page.expect_request('**/recruitingCEJobRequisitions**', timeout=15000):
                page.goto(careers_link, timeout=25000, wait_until='domcontentloaded')
            page.wait_for_timeout(500)
            captured['cookies'] = page.context.cookies()
            last_err = None
            break
        except Exception as e:
            last_err = e
        finally:
            if page:
                page.close()
    if last_err is not None:
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

    out = {}
    offset, limit = 0, 25
    for _ in range(20):
        api = base_api_url.format(offset=offset)
        status, text = jlib.fetch_static(api, extra_headers=session_headers)
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
            job_url = urljoin(base, f"/hcmUI/CandidateExperience/en/sites/{site_number or 'CX_1'}/job/{r.get('Id','')}")
            raw_title = r.get('Title', '')
            desc_parts = [
                r.get('ShortDescriptionStr', ''),
                r.get('ExternalQualificationsStr', ''),
                r.get('ExternalResponsibilitiesStr', ''),
            ]
            description = '\n\n'.join(p for p in desc_parts if p)
            dept = r.get('Department', '') or r.get('Organization', '')
            if r.get('PostingEndDate'):
                description += f"\n\nPosting closes: {r.get('PostingEndDate')}"
            out[job_url] = (raw_title, description, dept)
        offset += limit
        if len(reqs) < limit:
            break
        _time.sleep(0.3)
    return out


BULK_ADAPTERS = {
    'oracle': fetch_oracle_bulk,
}


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def _make_llm_client(use_llm):
    if not use_llm:
        return None
    import anthropic
    return anthropic.Anthropic()


def _classify_from_raw(school_id, links, ckpt, use_llm=False, llm_client=None):
    """Phase 2, shared by both orchestration paths below: once every
    posting's raw (title, description[, department]) is sitting in
    ckpt['raw'], corpus_stats can be built from ALL of them at once and
    every row classified against it -- this is why classification is a
    separate pass after fetching completes, not folded into the per-URL
    fetch loop above (TF-IDF against a corpus of one posting is
    meaningless)."""
    corpus_stats = None
    if not use_llm:
        items = [(raw['title'], raw['description']) for raw in ckpt['raw'].values() if 'error' not in raw]
        corpus_stats = build_corpus_stats(items)
    for url in links:
        raw = ckpt['raw'].get(url)
        if not raw:
            continue
        if 'error' in raw:
            ckpt['rows'][url] = {'error': raw['error']}
            continue
        ckpt['rows'][url] = classify_row(
            school_id, url, raw['title'], raw['description'], department=raw.get('department'),
            corpus_stats=corpus_stats, use_llm=use_llm, llm_client=llm_client)


def run_school_job_info(school_id, job_postings_checkpoint_path, job_info_checkpoint_path,
                         fetch_detail_fn=None, use_llm=False):
    """For a school with no BULK_ADAPTER: visits each posting URL
    individually via fetch_detail_fn (default fetch_detail_generic), then
    classifies once every posting's raw text is fetched (see
    _classify_from_raw). `use_llm`: whether area_key_words' supporting
    keywords come from an LLM call (needs ANTHROPIC_API_KEY / `ant auth
    login`) instead of the default local TF-IDF-against-this-school's-own-
    postings approach -- opt in once you have API credentials."""
    links = load_posting_links(job_postings_checkpoint_path)
    ckpt = load_checkpoint(job_info_checkpoint_path)
    ckpt.setdefault('raw', {})
    ckpt.setdefault('rows', {})
    ckpt['school_id'] = school_id
    ckpt['status'] = 'in_progress'
    ckpt['updated_at'] = now_iso()
    save_checkpoint(job_info_checkpoint_path, ckpt)

    def save_cb():
        ckpt['updated_at'] = now_iso()
        save_checkpoint(job_info_checkpoint_path, ckpt)
        write_info_csv(school_id, ckpt['rows'], links)

    try:
        to_fetch = [u for u in links if u not in ckpt['raw']]
        detail_fn = fetch_detail_fn or fetch_detail_generic
        for url in to_fetch:
            try:
                title, description = detail_fn(url)
                ckpt['raw'][url] = {'title': title, 'description': description}
            except Exception as e:
                ckpt['raw'][url] = {'error': f'{type(e).__name__}: {e}'}
            save_cb()
        _classify_from_raw(school_id, links, ckpt, use_llm=use_llm, llm_client=_make_llm_client(use_llm))
        ckpt['status'] = 'complete'
        ckpt['completed_at'] = now_iso()
        ckpt['last_error'] = ''
    except Exception as e:
        ckpt['status'] = 'error'
        ckpt['last_error'] = f'{type(e).__name__}: {e}'
    finally:
        save_cb()
    return ckpt


def run_school_job_info_bulk(school_id, careers_link, platform, job_postings_checkpoint_path,
                              job_info_checkpoint_path, use_llm=False):
    """For a school on a platform with a BULK_ADAPTER: one call gets every
    posting's info directly, rather than looping per-URL. `use_llm`: see
    run_school_job_info."""
    links = load_posting_links(job_postings_checkpoint_path)
    ckpt = load_checkpoint(job_info_checkpoint_path)
    ckpt.setdefault('raw', {})
    ckpt.setdefault('rows', {})
    ckpt['school_id'] = school_id
    ckpt['status'] = 'in_progress'
    ckpt['updated_at'] = now_iso()
    save_checkpoint(job_info_checkpoint_path, ckpt)

    def save_cb():
        ckpt['updated_at'] = now_iso()
        save_checkpoint(job_info_checkpoint_path, ckpt)
        write_info_csv(school_id, ckpt['rows'], links)

    try:
        adapter = BULK_ADAPTERS[platform]
        fetched = adapter(careers_link)
        for url in links:
            if url in ckpt['raw']:
                continue
            if url in fetched:
                title, description, department = fetched[url]
                ckpt['raw'][url] = {'title': title, 'description': description, 'department': department}
            else:
                ckpt['raw'][url] = {'error': 'not present in bulk fetch result'}
        save_cb()
        _classify_from_raw(school_id, links, ckpt, use_llm=use_llm, llm_client=_make_llm_client(use_llm))
        ckpt['status'] = 'complete'
        ckpt['completed_at'] = now_iso()
        ckpt['last_error'] = ''
    except Exception as e:
        ckpt['status'] = 'error'
        ckpt['last_error'] = f'{type(e).__name__}: {e}'
    finally:
        save_cb()
    return ckpt
