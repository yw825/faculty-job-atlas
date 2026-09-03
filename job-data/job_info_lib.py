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
# area_key_words: THREE parts, per explicit user instruction --
#   1. The subject named in the title itself: "Assistant Professor in X",
#      "Position in X", "... with a focus on X" and friends. Rule-based
#      (extract_primary_keyword) -- no ambiguity, it's literally there in
#      the title's rank clause.
#   2. Up to 2 keywords for WHAT RESEARCH the post is for, taken ONLY from
#      the sentences of the description that mention research.
#   3. 1 keyword for WHAT IS TAUGHT, taken ONLY from the sentences that
#      mention teach/teaches/teaching/taught.
#
# The user's preferred way to do 2 and 3 is an LLM reading those sentences
# (llm_extract_keywords, below), but neither this session nor the user has
# an ANTHROPIC_API_KEY ("I don't have API, so do whatever you can do
# best"), so the default is: restrict the candidate pool to the relevant
# sentences, then rank phrases in that pool by corpus-relative TF-IDF --
# how rare each phrase is across THIS SCHOOL'S OTHER postings' equivalent
# pool, not its raw frequency.
#
# Restricting the pool first is what makes this work. Scoring the WHOLE
# description (the previous approach) let a school's own name and its
# recruiting boilerplate compete with real subject matter and win --
# confirmed live on Sabanci University, whose keywords came out "analytics;
# sabanci; systems" and on Stockholm School of Economics, which produced
# "associate professors tenure-track; innovation management" for a posting
# whose actual research focus sentence says "Artificial Intelligence,
# Digital Health or Digital Resilience". A sentence that mentions research
# or teaching is far likelier to name a topic than a sentence about salary,
# closing dates, or how highly ranked the university is; TF-IDF then
# removes whatever admin phrasing those sentences still share across the
# school's postings. This is heuristic, not comprehension -- it finds what
# the research/teaching sentences are ABOUT by distinctiveness, it does not
# understand them. Set use_llm=True once API access exists for a real read.
# --------------------------------------------------------------------------

# A trigger word directly followed by a rank/role word ("Cluster **of**
# Assistant, Associate, or Full Professor Positions in X") isn't naming a
# subject at all -- it's describing the rank list -- so those words are
# excluded from starting a match; without this, this trigger (being first
# in the title) wins over the real "in X" clause later on and the real
# subject is lost entirely (confirmed live: Ohio-style cluster-hire titles
# like "...Cluster of Assistant, Associate, or Full Professor Positions in
# Geotechnical Engineering" produced "Assistant" instead of "Geotechnical
# Engineering").
_NON_SUBJECT_LEAD = (r'Assistant|Associate|Full|Professor|Professors|Lecturer|Senior|Instructor|'
                     r'Chair|Director|Dean|Faculty|Position|Positions|Fellow|Fellows|Adjunct|'
                     r'Visiting|Tenure|Tenured')

_RANK_SUBJECT_RE = re.compile(
    r'\b(?:in|of)\s+(?!(?:' + _NON_SUBJECT_LEAD + r')\b)([A-Z][A-Za-z0-9&,\'\s/-]{2,100}?)(?=\s*\(|$)')

# "with a focus on X" / "focusing on X" names the actual specialization more
# precisely than a generic "in/of" clause when both are present in the same
# title (confirmed live: Stockholm School of Economics -- "... Position in
# Information Systems and Innovation Management with a focus on Artificial
# Intelligence" -- the field the applicant actually cares about is the
# focus, not the broader department-level "in" clause), so it's tried first.
_FOCUS_SUBJECT_RE = re.compile(
    r'\b[Ff]ocus(?:ing)?\s+on\s+([A-Z][A-Za-z0-9&,\'\s/-]{2,100}?)(?=\s*\(|$)')

# A subject clause with no comma/paren/dash to stop at (many "own website"
# titles have none) runs on into trailing institution branding instead --
# confirmed live: Sabanci University's "... Position in Business Analytics &
# Information Systems Sabanci Business School, Sabanci University" has
# nothing separating the real subject from "Sabanci Business School" but a
# plain space. Rather than guess where the subject ends up front, capture
# generously (commas included, so a genuine enumerated subject like
# "Mathematics, Statistics and Insurance" survives whole) and strip a
# trailing "<Capitalized words> (University|College|School|Institute|
# Academy)" run off the end afterward -- applied in a loop since a name can
# be multiple such words deep ("Sabanci Business School"), and the leading
# separator can be a comma ("... School, Sabanci University") as well as
# plain whitespace.
_TRAILING_INSTITUTION_RE = re.compile(
    r'(?:[\s,]+(?:[A-Z][a-zA-Z]*\s+){0,2}(?:University|College|School|Institute|Academy))+\.?$')


def _strip_trailing_institution(text):
    prev = None
    while text and prev != text:
        prev = text
        text = _TRAILING_INSTITUTION_RE.sub('', text).strip()
    return text


# A subject clause with no comma/paren/dash to stop it can also run on into
# a full trailing sentence fragment instead of institution branding --
# confirmed live: "The Chair of Production Management is offering a
# part-time position as" (a mangled/truncated scrape of a German site's
# title) captured "Production Management is offering a part-time position
# as" whole. These verb-phrase markers don't appear in a genuine noun-phrase
# subject, so their presence means the capture ran past the real subject
# into surrounding sentence text -- safer to return nothing than something
# this wrong.
_NOT_A_SUBJECT_RE = re.compile(r'\b(?:is|will|offering|position\s+as|click\s+here)\b', re.I)


def extract_primary_keyword(title):
    """The subject named directly in the rank clause of the title, e.g.
    "Assistant Professor in Business Analytics" -> "Business Analytics",
    "Professor of Statistics" -> "Statistics". Only looks at the text
    before the first genuine clause-dash (a dash preceded by whitespace,
    ASCII hyphen or en/em dash -- Oracle-style titles append " - Department
    of X - <req id> - Grade N" after the role, and a hyphen with NO
    preceding space, like "BCC-Superalloys", is part of a compound word,
    not a clause break). Returns '' if the title states no explicit subject
    this way (many postings don't, e.g. "Research Fellow - Department of
    Pharmacy - ...")."""
    role_clause = re.split(r'\s[-–—]\s*', title, maxsplit=1)[0]
    m = _FOCUS_SUBJECT_RE.search(role_clause) or _RANK_SUBJECT_RE.search(role_clause)
    if not m:
        return ''
    subject = _strip_trailing_institution(m.group(1).strip())
    return '' if _NOT_A_SUBJECT_RE.search(subject) else subject


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


def _extract_candidate_phrases(text, max_n=3, extra_stopwords=None):
    """Splits text into runs of consecutive non-stopword tokens (a run
    breaks at any stopword or punctuation boundary), then emits every
    contiguous sub-run of length 1..max_n words as a candidate phrase --
    e.g. "gravitational wave astrophysics research" (after "research" is
    filtered as a stopword) yields "gravitational", "wave", "astrophysics",
    "gravitational wave", "wave astrophysics", "gravitational wave
    astrophysics". Returns a phrase -> count-in-this-text dict.

    A COMMA breaks a run too, so an enumerated list of topics ("artificial
    intelligence, machine learning, data mining, network analysis" --
    Sabanci University, verbatim) yields those four as separate phrases
    rather than cross-boundary nonsense like "intelligence machine
    learning". `extra_stopwords` adds pool-specific filler on top of
    _PHRASE_STOPWORDS (see _RESEARCH_ADMIN_STOPWORDS /
    _TEACHING_ADMIN_STOPWORDS)."""
    counts = {}
    stops = _PHRASE_STOPWORDS | extra_stopwords if extra_stopwords else _PHRASE_STOPWORDS
    for sentence_piece in re.split(r'[.;:,\n]', text or ''):
        tokens = _PHRASE_TOKEN_RE.findall(sentence_piece)
        run = []
        for tok in tokens + ['']:  # sentinel flushes the final run
            lw = tok.lower()
            if tok and lw not in stops and len(tok) >= 3:
                run.append(tok)
                continue
            for n in range(1, max_n + 1):
                for i in range(0, len(run) - n + 1):
                    phrase = ' '.join(run[i:i + n]).lower()
                    counts[phrase] = counts.get(phrase, 0) + 1
            run = []
    return counts


_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+|\n+')
_RESEARCH_SENT_RE = re.compile(r'\bresearch\w*\b', re.I)
_TEACH_SENT_RE = re.compile(r'\b(?:teach\w*|taught)\b', re.I)

# Words that show up INSIDE research/teaching sentences without ever being
# the topic -- the machinery of academic hiring rather than its subject
# ("publish in top-tier peer-reviewed journals", "teaching undergraduate
# and/or graduate courses"). Stopwording these matters for more than
# filtering: a run breaks at every stopword, so removing them is what
# splits "delivered university courses in management of digital
# technologies" down to the part that is actually a topic. Kept
# deliberately narrow -- anything that could plausibly BE somebody's field
# (network, design, systems, communication...) is left in and left to
# TF-IDF, which drops it anyway if the school's other postings share it.
_RESEARCH_ADMIN_STOPWORDS = set((
    'research researcher researchers researching teach teaches teaching taught '
    'publication publications publish publishing published journal journals '
    'peer-reviewed top-tier grant grants funding funded proposal proposals '
    'scholarly outlet outlets output outputs excellence world-class world-leading '
    'interest interests agenda portfolio pipeline record '
    'student students phd postgraduate undergraduate graduate doctoral doctorate '
    'master masters bachelor mba professor professors associate assistant lecturer '
    'tenure tenure-track fellow fellows fellowship postdoc postdocs postdoctoral '
    'scholar scholars collaboration collaborations collaborate collaborative '
    'partner partners area areas field fields concentration concentrations '
    'expertise emphasis focus focused focusing conduct conducting course courses '
    'letter cover curriculum vitae article articles submitted copies '
    'expected exhibit evidenced promising ranked ranking').split())

_TEACHING_ADMIN_STOPWORDS = set((
    'teach teaches teaching taught teacher teachers research researcher researchers '
    'course courses module modules class classes curriculum syllabus lecture lectures '
    'seminar seminars tutorial tutorials programme programmes program programs '
    'undergraduate graduate postgraduate doctoral doctorate master masters bachelor '
    'mba executive student students load levels delivered deliver delivering delivery '
    'supervise supervision supervising mentor mentoring coach coached '
    'duties responsibilities assessment assessments respective expertise '
    'service services profession competitive commensurate qualification qualifications '
    'professor professors associate assistant lecturer tenure tenure-track').split())

_POOLS = (('research', _RESEARCH_SENT_RE, _RESEARCH_ADMIN_STOPWORDS),
          ('teaching', _TEACH_SENT_RE, _TEACHING_ADMIN_STOPWORDS))


def _sentence_pool(description, sentence_pattern):
    """Only the sentences of a posting that actually mention the thing --
    research, or teaching. This is the whole point of the approach: the
    topic of a research post is stated in its research sentences, not in
    the paragraph about the pension scheme."""
    if not description:
        return ''
    # normalize non-breaking and other unicode spaces to plain ones -- they
    # otherwise survive every strip() with an explicit character set and
    # silently defeat the "starts with a verb" check (confirmed live on
    # Birmingham, where "\xa0build critical mass" got through as a topic)
    description = re.sub(r'\s+', ' ', description)
    return ' '.join(s.strip() for s in _SENTENCE_SPLIT_RE.split(description)
                    if sentence_pattern.search(s))


def _original_case(phrase, source_text):
    """Candidate phrases are lowercased for counting; show them back the
    way the posting actually wrote them ("Digital Health", not "digital
    health") when they can be found again in the source."""
    m = re.search(re.escape(phrase).replace(r'\ ', r'\s+'), source_text or '', re.I)
    return m.group(0) if m else phrase


def build_corpus_stats(items):
    """items: an iterable of (title, description) pairs, one per posting,
    for ALL of a school's postings in this run. Builds one document-
    frequency map PER POOL (research sentences, teaching sentences), so a
    phrase is judged against the equivalent sentences of that school's
    other postings -- "publish in leading journals" is ubiquitous among
    research sentences and scores ~0, while the posting's actual topic is
    rare and scores high. Document frequency is relative to THIS school's
    own postings, which is what catches its own repeated boilerplate
    regardless of what phrasing convention it uses."""
    stats = {}
    for key, sentence_pattern, extra_stopwords in _POOLS:
        n_docs = 0
        doc_freq = {}
        for _title, description in items:
            pool = _sentence_pool(description, sentence_pattern)
            if not pool.strip():
                continue
            n_docs += 1
            for phrase in _extract_candidate_phrases(pool, extra_stopwords=extra_stopwords):
                doc_freq[phrase] = doc_freq.get(phrase, 0) + 1
        stats[key] = {'n_docs': n_docs, 'doc_freq': doc_freq}
    return stats


# Topic-introducing phrases: what a human scanning these sentences actually
# reads to answer "what research is this?" / "what would I teach?". Each is
# paired with a precision tier -- a span introduced by "research focus on"
# is far likelier to BE the topic than one introduced by a bare "including",
# which is just as often listing a university's breadth as this post's
# subject. The captured span is the grammatical object; cleanup below trims
# it back to the topic itself.
_RESEARCH_TOPIC_PATTERNS = (
    (r'research\s+(?:focus|focuses|focusing|interests?|expertise|experience|area|areas|'
     r'agenda|programme|program|activities|profile|strengths?)\s*(?:is|are|will\s+be)?\s*'
     r'(?:on|in|of|within|into)\s+(.{3,160})', 1.0),
    (r'\bresearch\s+(?:in|on|into|within)\s+(.{3,160})', 1.0),
    (r'\b(?:expertise|specialis\w+|specializ\w+|background|track\s+record)\s+in\s+(.{3,160})', 1.0),
    (r'\bconduct(?:ing|s)?\s+research\s+(?:on|in|into)\s+(.{3,160})', 1.0),
    (r'\bwork(?:ing)?\s+(?:on|in)\s+the\s+(?:area|field)s?\s+of\s+(.{3,160})', 1.0),
    (r'\bareas?\s+of\s+(.{3,160})', 0.5),
    (r'\bfields?\s+of\s+(.{3,160})', 0.5),
    (r'\bincluding\s+(.{3,160})', 0.0),
)

_TEACHING_TOPIC_PATTERNS = (
    (r'\bteach(?:ing)?\s+(?:in|of)\s+(.{3,160})', 1.0),
    (r'\b(?:courses?|modules?|classes|programmes?|programs?)\s+(?:in|on)\s+(.{3,160})', 1.0),
    (r'\bdeliver(?:ing|ed)?\s+(?:courses?|modules?|teaching)\s+(?:in|on)\s+(.{3,160})', 1.0),
    # the capital is scoped case-sensitive: these patterns run under re.I,
    # which would otherwise let "teaching load and salary..." match here
    (r'\bteach(?:es|ing)?\s+((?-i:[A-Z])[A-Za-z&\-/ ]{2,60})', 0.5),
    (r'\bincluding\s+(.{3,160})', 0.0),
)

# Everything from here on in a captured span belongs to the next clause, not
# to the topic ("Digital Resilience will be considered a plus" -> "Digital
# Resilience").
_CLAUSE_BREAK_RE = re.compile(
    r'[.!?()\[\]]|\b(?:will|is|are|was|were|would|should|shall|can|could|may|might|must|'
    r'has|have|had|that|which|who|whom|whose|where|when|while|as|to|for|from|by|with|at|but|'
    r'in|into|within|through|during|across|among|between|per|via|about|'
    r'evidenced|considered|required|preferred|expected|demonstrated|desirable|essential|'
    r'etc|beyond|others|more|plus|advantage|asset)\b', re.I)

# Stripped repeatedly off the FRONT of a span, so "one or more concentration
# areas of business analytics" reduces to "business analytics".
_LEADING_FILLER_RE = re.compile(
    r'^(?:the|a|an|one|two|three|any|all|both|either|some|several|various|other|more|most|'
    r'related|relevant|following|broad|broadly|core|key|main|specific|specialised|specialized|'
    r'areas?|fields?|topics?|domains?|disciplines?|subjects?|concentrations?|'
    r'specialisations?|specializations?|aspects?|of|in|on|and|or|its|their|our|his|her|'
    r'undergraduate|graduate|postgraduate|doctoral|masters?|bachelors?|mba|executive|'
    r'courses?|modules?|classes|programmes?|programs?|levels?|students?|'
    r'including|include|includes|included|such|as|e\.?g\.?|i\.?e\.?|'
    r'strong|excellent|proven|demonstrable|significant|substantial|high[- ]quality|'
    r'new|emerging|innovative|world[- ]class|leading|international|national)\b[\s,]*', re.I)

_SPLIT_ITEMS_RE = re.compile(r',|\band/or\b|\band\b|\bor\b|;|/|&', re.I)

# An "item" made only of these is administrative vocabulary, not a subject.
_ADMIN_ONLY_WORDS = set((
    'research teaching education study studies work position post role service '
    'excellence quality experience expertise knowledge skills ability abilities '
    'university school college faculty department institute centre center '
    'students student staff members community environment activities '
    'publication publications journals grants funding projects project '
    'related relevant respective various other others topics areas fields topic area '
    'discipline disciplines subject subjects level levels field domain domains '
    'application applications statement statements vitae curriculum letter letters '
    'reference references contact information philosophy plans plan accomplishments '
    'portfolio load salary profession culture engagement opportunities partners '
    'network networks ecosystem candidates candidate appointment employment '
    'documents document copies interests interest agenda record profile '
    'mentoring supervision collaboration collaborations development training '
    'income budget revenue resources infrastructure facilities equipment '
    'importance impact reputation standing visibility ambition ambitions '
    'commitment evidence understanding approach practice practices '
    'group groups team teams unit units programme program').split())

# Sentences telling the APPLICANT what to send describe the application, not
# the job -- confirmed live on AcademicJobsOnline postings, whose only
# "research" sentences are "Research statement describing past research
# accomplishments and future research plans".
_INSTRUCTION_SENT_RE = re.compile(
    r'\b(?:submit|upload|send|attach|enclose|provide\s+(?:a|the|your)|'
    r'cover\s+letter|curriculum\s+vitae|\bcv\b|letters?\s+of\s+(?:reference|recommendation)|'
    r'statement\s+(?:of|describing)|please\s+(?:apply|include)|'
    r'application\s+(?:should|must|materials))\b', re.I)

# A topic span that starts with a verb is a duty, not a subject
# ("...areas of statistics to build critical mass, strengthen the group's
# national profile and develop interdisciplinary..." -- Birmingham,
# verbatim, which yielded "build critical mass" and "strengthen the
# group's national" before this filter).
_LEADING_VERB_RE = re.compile(
    r'^(?:build|strengthen|develop|deliver|support|lead|establish|contribute|undertake|'
    r'carry|conduct|engage|work|promote|enhance|expand|maintain|participate|publish|'
    r'secure|attract|drive|foster|create|provide|ensure|help|join|produce|generate|'
    r'pursue|advance|grow|improve|increase|manage|coordinate|supervise|collaborate|'
    r'disseminate|present|write|prepare|assist|apply|make|take|bring|play|inform)\b', re.I)

# Below this, a candidate isn't good enough to publish -- an empty
# area_key_words slot beats a confidently wrong one. Set so that a bare
# single word introduced by a weak pattern ("...including commensurate")
# can't qualify, while a multi-word phrase from a weak pattern
# ("...including artificial intelligence") can.
_TOPIC_SCORE_FLOOR = 1.5

# A phrase this much of a school's postings share is its house boilerplate,
# not this posting's topic -- Aston repeats "research in areas such as
# engineering, medicine, social sciences and humanities" in 11 of its 19
# postings.
_BOILERPLATE_DF_RATIO = 0.5


# A school's own name and acronym are never the subject of its own job ad,
# but they are all over its page furniture -- confirmed live: UCL's
# navigation produced "Examination Support Department UCL BEAMS" as a
# taught subject, and Sabanci University's own name kept surfacing as a
# keyword. Corpus rarity does NOT catch these reliably: "ucl beams" appears
# in exactly one posting, so it looks maximally distinctive. The name comes
# from schools_master.csv keyed by school_id, so no per-school script needs
# to pass anything.
_GENERIC_NAME_WORDS = frozenset((
    'university universities college school schools institute institution academy '
    'centre center polytechnic technology technological national state the of and '
    'für fur de la del di du des van der och').split())

# Words that turn up in institution names but are also perfectly good
# subjects -- never let these become identity tokens, or "Economics" gets
# thrown away as a topic at the Stockholm School of Economics.
_NAME_FIELD_WORDS = frozenset((
    'economics business management technology science sciences engineering arts '
    'humanities medicine medical law education health music design agriculture '
    'mathematics physics chemistry biology philosophy theology divinity veterinary '
    'nursing pharmacy dentistry architecture computing informatics communication '
    'journalism finance accounting marketing psychology').split())

_SCHOOL_NAMES = None


def _school_name(school_id):
    global _SCHOOL_NAMES
    if _SCHOOL_NAMES is None:
        _SCHOOL_NAMES = {}
        try:
            with open(os.path.join(HERE, 'schools_master.csv'), encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    try:
                        _SCHOOL_NAMES[int(row['school_id'])] = row.get('name') or ''
                    except (KeyError, TypeError, ValueError):
                        continue
        except OSError:
            pass
    return _SCHOOL_NAMES.get(school_id, '')


# Letters that NFKD can't decompose into base+accent still need folding, or
# "Sabanci" in the page text won't match "Sabancı" from the school name.
_LETTER_FOLD = str.maketrans({'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 'ş': 's', 'Ş': 'S',
                              'ø': 'o', 'Ø': 'O', 'ł': 'l', 'Ł': 'L', 'đ': 'd', 'Đ': 'D',
                              'æ': 'ae', 'Æ': 'AE', 'œ': 'oe', 'Œ': 'OE', 'ß': 'ss'})


def _ascii_fold(text):
    import unicodedata
    folded = (text or '').translate(_LETTER_FOLD)
    return ''.join(c for c in unicodedata.normalize('NFKD', folded)
                   if not unicodedata.combining(c))


def school_identity_tokens(school_id):
    """The school's own distinctive name words plus its acronym, lowercased
    and diacritic-folded ("Sabanci University" -> {"sabanci"}, "University
    College London" -> {"london", "ucl"})."""
    name = _school_name(school_id)
    if not name:
        return frozenset()
    words = [w.lower() for w in re.findall(r"[A-Za-z\u00C0-\u024F']+", _ascii_fold(name))]
    tokens = {w for w in words
              if len(w) >= 3 and w not in _GENERIC_NAME_WORDS and w not in _NAME_FIELD_WORDS}
    acronym = ''.join(w[0] for w in words if len(w) >= 3 and w not in ('the', 'and', 'for'))
    if len(acronym) >= 3:
        tokens.add(acronym)
    return frozenset(tokens)


def _is_school_identity(item, identity_tokens):
    """True when the candidate is the school talking about itself: it
    carries the acronym, or every one of its words is part of the school's
    name. Deliberately NOT "contains any name word" -- that would throw
    away "Chinese literature" at the Chinese University of Hong Kong."""
    if not identity_tokens:
        return False
    words = [w.lower() for w in re.findall(r"[A-Za-z\u00C0-\u024F']+", _ascii_fold(item))]
    if not words:
        return False
    # a short name token on its own is enough -- an acronym ("ucl") or a
    # one-word institution name is never part of a real subject
    if any(len(w) <= 5 and w in identity_tokens for w in words):
        return True
    return all(w in identity_tokens or w in _GENERIC_NAME_WORDS for w in words)


# Short words that legitimately sit inside a topic ("management OF digital
# technologies") -- every other 1-2 letter token means the span was cut
# mid-phrase or picked up an initialism from page furniture ("AEP
# equivalent up", "Posts GU").
_SHORT_CONNECTORS = frozenset(('of in on at to for and or the a an de la di du el &').split())


# A topic never contains markup, money, a date or site navigation -- these
# turn up when a description carries raw page furniture (confirmed live:
# "clinical departments<; li><li>Work", "salary of $140", "Monday 25th
# January 2027; followed", "Technician Skip").
_JUNK_ITEM_RE = re.compile(
    r'[<>$£€%@|{}]|\d|'
    r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|'
    r'january|february|march|april|june|july|august|september|october|november|december|'
    r'skip|menu|login|log\s*in|sign\s*in|portal|homepage|cookies?|privacy|copyright|'
    r'newsletter|footer|header|breadcrumb|sitemap|navigation)\b', re.I)


def _clean_topic_item(item):
    item = item.strip(' \t\n\r,.;:*-–—()[]"\'')
    if _LEADING_VERB_RE.match(item):
        return ''
    prev = None
    while prev != item:
        prev = item
        item = _LEADING_FILLER_RE.sub('', item).strip(' ,.;:-')
    m = _CLAUSE_BREAK_RE.search(item)
    if m:
        item = item[:m.start()].strip(' ,.;:-')
    item = ' '.join(item.split()[:5]).strip(' ,.;:-')
    if len(item) < 4 or _JUNK_ITEM_RE.search(item):
        return ''
    if all(w.lower().strip('.,') in _ADMIN_ONLY_WORDS for w in item.split()):
        return ''
    words = item.split()
    if len(words) > 1 and any(len(w.strip('.,&/-')) < 3 and w.lower().strip('.,&/-')
                              not in _SHORT_CONNECTORS for w in words):
        return ''
    return item


def _drop_instruction_sentences(pool):
    return ' '.join(s for s in _SENTENCE_SPLIT_RE.split(pool or '')
                    if s.strip() and not _INSTRUCTION_SENT_RE.search(s))


def _topic_candidates(pool, patterns):
    """Every topic named in `pool` by one of `patterns`, as
    (item, best pattern tier) -- keeping the highest tier when the same
    item is found by more than one pattern."""
    best = {}
    for pattern, tier in patterns:
        for m in re.finditer(pattern, pool, re.I):
            span = m.group(1)
            # never read past the end of the sentence the topic was named in
            # (a fixed-width capture otherwise runs into the next sentence:
            # "...courses in the respective fields. The teaching load and
            # salary are competitive and commensurate..." yielded
            # "commensurate" as a taught subject), and drop a trailing
            # partial word left by the capture's own width limit.
            span = re.split(r'[.;!?]', span)[0]
            if not span.endswith(' ') and ' ' in span and len(m.group(1)) >= 160:
                span = span[:span.rfind(' ')]
            for raw in _SPLIT_ITEMS_RE.split(span):
                item = _clean_topic_item(raw)
                if not item:
                    continue
                key = item.lower()
                if key not in best or tier > best[key][1]:
                    best[key] = (item, tier)
    return list(best.values())


def _item_doc_freq(item, doc_freq, extra_stopwords=None):
    """How many of the school's postings share this candidate. Corpus stats
    only hold phrases up to 3 words and only between stopwords, so a longer
    or stopword-spanning candidate isn't in the map at all and would look
    maximally rare no matter how much boilerplate it is -- confirmed live on
    UCL, whose page navigation yielded "Examination Support Department UCL
    BEAMS" as a taught subject. Fall back to the item's own LONGEST
    constituent phrases: for that navigation string those are "ucl beams",
    in every UCL posting, while for a real topic like "Digital Health" the
    longest constituent is the topic itself. (Taking the max over ALL
    constituents instead would over-suppress, since a real topic's
    individual words are often common on their own.)"""
    key = item.lower()
    if key in doc_freq:
        return doc_freq[key]
    phrases = _extract_candidate_phrases(item, extra_stopwords=extra_stopwords)
    if not phrases:
        return 0
    longest = max(len(p.split()) for p in phrases)
    return max(doc_freq.get(p, 0) for p in phrases if len(p.split()) == longest)


def topic_keywords(pool, patterns, pool_stats, exclude_terms=(), max_keywords=2,
                   extra_stopwords=None, identity_tokens=frozenset()):
    """Rank the topics named in one sentence pool. Score combines:
      - pattern tier (how reliably that phrasing introduces a real topic),
      - whether the posting capitalizes it (field names usually are),
      - rarity across this school's other postings' equivalent pool,
      - a small bonus for multi-word phrases (more specific).
    A phrase most of the school's postings share is dropped outright as
    house boilerplate, and anything scoring under _TOPIC_SCORE_FLOOR is
    dropped rather than published."""
    n = (pool_stats or {}).get('n_docs', 0)
    doc_freq = (pool_stats or {}).get('doc_freq', {})
    excluded = [e.lower() for e in exclude_terms if e]

    scored = []
    for item, tier in _topic_candidates(pool, patterns):
        low = item.lower()
        if any(low in e or e in low for e in excluded):
            continue
        if _is_school_identity(item, identity_tokens):
            continue
        df = _item_doc_freq(item, doc_freq, extra_stopwords)
        if n >= 2 and df / max(n, 1) >= _BOILERPLATE_DF_RATIO:
            continue
        rarity = 1.0 if n < 2 else 1.0 - (df / max(n, 1))
        capitalized = 1.0 if (item[:1].isupper() and not item.isupper()) else 0.0
        specific = 0.5 if len(item.split()) > 1 else 0.0
        score = tier + capitalized + rarity + specific
        if score >= _TOPIC_SCORE_FLOOR:
            scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], -len(x[1]), x[1].lower()))
    out = []
    for _score, item in scored:
        if any(item.lower() in k.lower() or k.lower() in item.lower() for k in out):
            continue
        out.append(item)
        if len(out) >= max_keywords:
            break
    return out


def extract_keywords(title, description='', corpus_stats=None, use_llm=False, llm_client=None,
                     school_id=None):
    """area_key_words, in the three parts specified for this project (see
    the block comment above extract_primary_keyword):

      1. the subject named in the title's own rank clause;
      2. up to 2 keywords for what research the post is for, read out of
         the description's research sentences only;
      3. 1 keyword for what it wants taught, read out of its teaching
         sentences only.

    Parts 2 and 3 come from llm_extract_keywords instead when use_llm=True
    (needs API credentials -- opt in once you have them). A part is simply
    absent when the posting doesn't support one: a posting with no teaching
    sentences, or whose teaching sentences only discuss workload and
    salary, gets no teaching keyword rather than a filler scraped from
    unrelated text."""
    primary = extract_primary_keyword(title)
    keywords = [primary] if primary else []

    if use_llm:
        try:
            supporting = llm_extract_keywords(title, description, primary, client=llm_client)
            return '; '.join(keywords + [s for s in supporting if s.lower() != primary.lower()])
        except Exception:
            pass

    if not corpus_stats:
        return '; '.join(keywords)

    exclude = list(keywords)
    identity_tokens = school_identity_tokens(school_id) if school_id else frozenset()
    for key, sentence_pattern, _stopwords in _POOLS:
        pool = _drop_instruction_sentences(_sentence_pool(description, sentence_pattern))
        patterns = _RESEARCH_TOPIC_PATTERNS if key == 'research' else _TEACHING_TOPIC_PATTERNS
        found = topic_keywords(pool, patterns, corpus_stats.get(key), exclude_terms=exclude,
                               max_keywords=2 if key == 'research' else 1,
                               extra_stopwords=_stopwords, identity_tokens=identity_tokens)
        keywords.extend(found)
        exclude.extend(found)
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
                                            use_llm=use_llm, llm_client=llm_client,
                                            school_id=school_id),
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


def fetch_smartrecruiters_bulk(careers_link):
    """Returns {posting_url: (title, description, department)} from
    SmartRecruiters' public REST API. The listing call already carries the
    title, department and location for every posting; only the description
    needs a per-posting call, and that call returns clean structured
    sections rather than a page whose visible text is mostly chrome."""
    import time as _time
    from html import unescape

    m = re.search(r'smartrecruiters\.com/([^/?#]+)', careers_link)
    if not m:
        raise RuntimeError('could not parse smartrecruiters company slug')
    company = m.group(1)

    out = {}
    offset, limit = 0, 100
    for _ in range(20):
        api = (f'https://api.smartrecruiters.com/v1/companies/{company}'
               f'/postings?limit={limit}&offset={offset}')
        status, text = jlib.fetch_static(api, extra_headers={'Accept': 'application/json'})
        if status != 200:
            break
        data = json.loads(text)
        content = data.get('content', [])
        if not content:
            break
        for item in content:
            posting_id = item.get('id', '')
            if not posting_id:
                continue
            url = f'https://jobs.smartrecruiters.com/{company}/{posting_id}'
            title = item.get('name', '') or ''
            dept = (item.get('department') or {}).get('label', '') or ''
            description = ''
            d_status, d_text = jlib.fetch_static(
                f'https://api.smartrecruiters.com/v1/companies/{company}/postings/{posting_id}',
                extra_headers={'Accept': 'application/json'})
            if d_status == 200:
                try:
                    sections = json.loads(d_text).get('jobAd', {}).get('sections', {})
                except ValueError:
                    sections = {}
                parts = []
                for key in ('jobDescription', 'qualifications', 'additionalInformation',
                            'companyDescription'):
                    body = (sections.get(key) or {}).get('text', '')
                    if body:
                        parts.append(unescape(re.sub(r'<[^>]+>', ' ', body)))
                description = re.sub(r'[ \t]+', ' ', '\n\n'.join(parts)).strip()
            out[url] = (title, description, dept)
            _time.sleep(0.15)
        offset += limit
        if offset >= data.get('totalFound', 0):
            break
        _time.sleep(0.3)
    return out


BULK_ADAPTERS = {
    'oracle': fetch_oracle_bulk,
    'smartrecruiters': fetch_smartrecruiters_bulk,
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
