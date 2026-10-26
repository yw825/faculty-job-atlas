"""Which rank box a faculty posting belongs in, read the way each country's
academic system means its titles.

The map offers five classes:

  Assistant_Professor  entry rank of the research-and-teaching career track
                       (tenure-track, or the permanent track where there is no
                       tenure)
  Associate_Professor  middle rank of that track
  Full_Professor       top rank (incl. named and chair professorships)
  Lecturer             "Lecturer / Teaching": teaching-focused, non-tenure-
                       track, clinical, practice, visiting, adjunct and
                       part-time appointments
  Research_Fellow      "Research Fellow / Postdoc": postdocs, research
                       fellows/associates/scientists, research-track faculty

The same word means different things in different systems, so the posting's
country picks the system:

  North American (US, Canada; also the default)
    Assistant / Associate / (Full) Professor ........ the three ranks
    "Professor of Practice", "Clinical", "Teaching" or "Instructional"
    Professor, "Visiting", "Adjunct", "Affiliate", "Professional-track",
    "Teaching Stream", Lecturer, Instructor, Pro Tem, Sessional,
    part-time, and any post the advert calls non-tenure-track .... Teaching
    "Research" Assistant/Associate Professor ........ Research
  British (UK, Ireland, Australia, New Zealand)
    Lecturer (Level B) ..... Assistant      Senior Lecturer (Level C), Reader,
    Principal Lecturer ..... Associate      Professor ...... Full
    Assistant / Associate Professor (the newer titles) as named
    Teaching Fellow, Associate Lecturer, "Teaching and Scholarship",
    "Education-focused" ................................ Teaching
  Asian (Hong Kong, Singapore, Macau)
    Assistant / Associate / Chair Professor as named
    Lecturer, Senior Lecturer, Instructor, Educator track .. Teaching
    Research Assistant Professor ........................... Research
  Continental European
    Assistant Professor, Tenure-Track Professor, Juniorprofessor (W1),
    Universitair Docent, Adjunkt (DK), Biträdande lektor (SE), Maître de
    conférences, Profesor Ayudante Doctor, Ricercatore tenure-track
    (RTT / RTD-b) .............................................. Assistant
    Associate Professor, W2, Universitair Hoofddocent, Lektor (DK/NO),
    Universitetslektor / Senior Lecturer (SE), Profesor Titular /
    Contratado Doctor, Professore Associato ..................... Associate
    Professor, W3, Catedrático, Professore Ordinario, Professeur des
    universités ................................................. Full
    Lecturer, Teacher, Docent (teaching), Profesor Asociado (Spain's
    part-time post, NOT an associate professorship) ............. Teaching
    Postdoc, Researcher, RTD-a ................................... Research

A posting can sit in several boxes: "Open Rank" is all three professorial
ranks; "Assistant/Associate Professor" both; "Assistant Professor
(Tenure-Track) or Assistant Professor of Practice" is Assistant AND
Teaching.
"""
import re

ASST, ASSOC, FULL = 'Assistant_Professor', 'Associate_Professor', 'Full_Professor'
TEACH, RESEARCH = 'Lecturer', 'Research_Fellow'
PROF_RANKS = [ASST, ASSOC, FULL]
ORDER = [ASST, ASSOC, FULL, TEACH, RESEARCH]

_BRITISH = {'United Kingdom', 'UK', 'Ireland', 'Australia', 'New Zealand'}
_ASIAN = {'Hong Kong', 'Singapore', 'Macau', 'Macao'}
_NORTH_AMERICAN = {'US', 'USA', 'United States', 'Canada', ''}


def system_for(country):
    country = (country or '').strip()
    if country in _BRITISH:
        return 'british'
    if country in _ASIAN:
        return 'asian'
    if country in _NORTH_AMERICAN:
        return 'north_american'
    return 'european'


def _rx(p):
    return re.compile(p, re.I)


# Pieces of a title that hold one appointment each: "A or B", "A; B",
# "A – B". A professor phrase's modifiers are read inside its own piece only,
# so "Assistant Professor (Tenure-Track) or Assistant Professor of Practice"
# is one tenure-track post and one teaching post.
_SEPARATORS = _rx(r'\s+or\s+|;|\s[-–—]\s|\||\s/\s')

_PROFESSOR = _rx(r'\bprof(?:essor|essorship)?s?\b\.?')
_TEACHING_MOD = _rx(
    r'\bof\s+(?:the\s+)?practice\b|\bclinical\b|\bteaching\b|\binstructional\b|\bvisiting\b|'
    r'\badjunct\b|\baffiliate\b|\beducator\b|\bprofessional[- ]track\b|\bpractice[- ]track\b|'
    r'\bnon[- ]?tenure|\bpart[- ]time\b|\bprofessor\s+of\s+teaching\b|\blecturer[- ]track\b')
_RESEARCH_MOD = _rx(r'\bresearch\s+(?:assistant\s+|associate\s+|full\s+)?prof|'
                    r'\bresearch[- ](?:track|faculty|stream)\b|\(research\)')
_TENURE = _rx(r'(?<!non-)(?<!non\s)(?<!non)\btenure[- ]?(?:track|line|system|stream|eligible)|'
              r'\btenured\b|\bW[123]\b')

_ASST_WORD = _rx(r'\b(?:assistant|asst|ast|junior|juniorprofessor)\b\.?|\btenure[- ]?track\s+prof')
_ASSOC_WORD = _rx(r'\b(?:associate|assoc|asc)\b\.?')
_FULL_WORD = _rx(r'\bfull\b(?![- ]?time)|\bchair\b|\bdistinguished\b|\bendowed\b|\beminent\b|\bnamed\b|'
                 r'\bprofessorship\b')
_OPEN_RANK = _rx(r'\bopen[- ]?rank|\b(?:all|any)\s+(?:academic\s+)?(?:ranks?|levels?)\b|'
                 r'\brank\s+open\b')

# Local titles, read as the rank they are rather than the English word they
# resemble.
_LOCAL = [
    (_rx(r'\bprofesor(?:a)?\s+asociad[oa]\b'), [TEACH]),
    (_rx(r'\bprofesor(?:a)?\s+ayudante\s+doctor'), [ASST]),
    (_rx(r'\bprofesor(?:a)?\s+(?:titular|contratad[oa]\s+doctor)'), [ASSOC]),
    (_rx(r'\bcatedr[aá]tic[oa]\b'), [FULL]),
    (_rx(r'\bprofessore\s+associato\b'), [ASSOC]),
    (_rx(r'\bprofessore\s+ordinario\b'), [FULL]),
    (_rx(r'\bricercator[ei]\b.{0,40}\b(?:tenure|RTT|RTD[- ]?b|tipo\s+b)\b|\bRTT\b|\bRTD[- ]?b\b'), [ASST]),
    (_rx(r'\bRTD[- ]?a\b|\bricercator[ei]\s+a\s+tempo\s+determinato\b'), [RESEARCH]),
    (_rx(r'\bma[iî]tre\s+de\s+conf[ée]rences\b'), [ASST]),
    (_rx(r'\bprofesseur\s+des\s+universit[ée]s\b'), [FULL]),
    (_rx(r'\bjuniorprofessur|\bW1\b'), [ASST]),
    (_rx(r'\bW2\b'), [ASSOC]),
    (_rx(r'\bW3\b'), [FULL]),
    (_rx(r'\buniversitair\s+hoofddocent\b'), [ASSOC]),
    (_rx(r'\buniversitair\s+docent\b'), [ASST]),
    (_rx(r'\bbitr[äa]dande\s+(?:universitets)?lektor\b'), [ASST]),
    (_rx(r'\buniversitetslektor\b|\bf[øo]rsteamanuensis\b'), [ASSOC]),
    (_rx(r'\badjunkt\b'), [ASST]),
    (_rx(r'\blektor\b'), [ASSOC]),
]

_LECTURER = _rx(r'\blecturers?\b|\blectureship\b')
_SENIOR_LECT = _rx(r'\b(?:senior|principal)\s+lecturers?\b')
_ASSOC_LECT = _rx(r'\b(?:associate|assistant)\s+lecturers?\b')
_READER = _rx(r'\breader\b')
_BRITISH_TEACHING = _rx(r'\bteaching\s+(?:fellow|associate|and\s+scholarship|focused|track)|'
                        r'\beducation[- ](?:focused|and\s+scholarship|track)|'
                        r'\(teaching\)|\bteaching[- ]only\b|\bteaching[- ]intensive\b')
_TEACHING_ROLE = _rx(
    r'\binstructors?\b|\badjunct\b|\bpro\s+tem\b|\bsessional\b|\btutors?\b|\bdemonstrators?\b|'
    r'\bteachers?\b|\bteaching\s+(?:fellow|faculty|stream|track|position|staff)|\bpart[- ]time\b|'
    r'\bcourse\s+(?:instructor|lecturer)\b|\bclinical\b|\bprofessional[- ]track\b|'
    r'\bnon[- ]?tenure|\baffiliate\s+faculty\b|\bvisiting\b')
_RESEARCH_ROLE = _rx(
    r'\bpost[- ]?doc\w*|\bresearch\s+(?:fellow|associate|scientist|professional|faculty|engineer)|'
    r'\bscientists?\b|\bresearchers?\b|\bfellow(?:s|ship|ships)?\b|\bgroup\s+leader\b|'
    r'\bwissenschaftliche')
_CHAIR = _rx(r'\b(?:endowed|eminent|distinguished)\b.*\b(?:chair|professorship)\b|'
             r'\bdepartment\s+chair\b|\bchair\s+(?:and|&)\s+professor\b|\bchair\s+professor\b')
_FACULTY = _rx(r'\bfaculty\b|\bprofessorships?\b|\bpositions?\b|\btenure[- ]?track\b|\bopenings?\b')

# Advert-text signals, used for North American posts whose title says only
# "Assistant Professor of X": many say "full-time, non-tenure-track" only
# in the body.
_DESC_NTT = _rx(
    r'\bnon[- ]?tenure[- ]?(?:track|eligible|line|stream|system)|\bnot\s+(?:a\s+)?tenure[- ]?track|'
    r'\bteaching[- ](?:track|stream|focused|intensive)\s+(?:position|faculty|appointment|role)|'
    r'\bprofessional[- ]track\b|\bclinical[- ]track\b|\bpractice[- ]track\b')
_DESC_TT = _rx(r'(?<!non-)(?<!non\s)(?<!non)\btenure[- ]?(?:track|line|system|eligible)\b|'
               r'\btenured\b|\bwith\s+tenure\b')


def _pieces(title):
    return [p for p in _SEPARATORS.split(title) if p and p.strip()]


def _professor_ranks(piece):
    """Ranks named in one title piece that contains a professor phrase."""
    ranks = []
    if _OPEN_RANK.search(piece):
        return list(PROF_RANKS)
    if _ASST_WORD.search(piece):
        ranks.append(ASST)
    if _ASSOC_WORD.search(piece):
        ranks.append(ASSOC)
    if _FULL_WORD.search(piece):
        ranks.append(FULL)
    # a bare "Professor" left over beside junior ranks is its own rank
    # ("Chair Professor/Professor/Associate Professor/Assistant Professor")
    residue = re.sub(r'(?i)\b(?:assistant|asst|ast|associate|assoc|asc|full|research|teaching|'
                     r'clinical|visiting|adjunct|instructional|chair)\b\.?\s*/?\s*', ' ', piece)
    if not ranks:
        ranks.append(FULL)
    elif FULL not in ranks and re.search(r'(?i)(?:^|/|,)\s*professor\b', residue) and \
            len(_PROFESSOR.findall(piece)) > 1:
        ranks.append(FULL)
    return ranks


def classify_rank(title, description='', country=''):
    """List of rank classes (ORDER) for one posting, or ['Unclassified']."""
    title = re.sub(r'\s+', ' ', title or '').strip()
    description = description or ''
    system = system_for(country)
    out = []

    def add(*vals):
        for v in vals:
            if v not in out:
                out.append(v)

    plain_prof = False
    for piece in _pieces(title):
        if any(rx.search(piece) for rx, _ in _LOCAL):
            for rx, vals in _LOCAL:
                if rx.search(piece):
                    add(*vals)
                    if vals != [TEACH] and vals != [RESEARCH]:
                        plain_prof = True
            continue
        if _PROFESSOR.search(piece):
            ranks = _professor_ranks(piece)
            if _RESEARCH_MOD.search(piece) and not _TENURE.search(piece):
                add(RESEARCH)
            elif _TEACHING_MOD.search(piece) and not _TENURE.search(piece):
                add(TEACH)
            else:
                add(*ranks)
                plain_prof = True
            # "Instructor/Assistant/Associate/Full Professor": the instructor
            # is a separate appointment in the same piece
            if re.search(r'(?i)\binstructor\b|\blecturer\b', piece):
                add(TEACH)
            if re.search(r'(?i)\bpost[- ]?doc', piece):
                add(RESEARCH)
            continue
        if _OPEN_RANK.search(piece):
            # "Open Rank - Fixed Term - (Assistant/Associate/Full) Teaching
            # Professor", "Faculty Position (Open Rank), Non-tenure Track",
            # "Research Professorial Open Rank": the open rank is of the
            # teaching or research post the rest of the title names.
            if not _TENURE.search(title) and (_RESEARCH_MOD.search(title)
                                              or re.search(r'(?i)\bresearch\s+professorial', title)):
                add(RESEARCH)
            elif not _TENURE.search(title) and (_TEACHING_MOD.search(title)
                                                or _TEACHING_ROLE.search(title)):
                add(TEACH)
            else:
                add(*PROF_RANKS)
                plain_prof = True
            continue
        if _LECTURER.search(piece):
            if system == 'british' and not _BRITISH_TEACHING.search(piece):
                if _ASSOC_LECT.search(piece):
                    add(TEACH)
                if _SENIOR_LECT.search(piece):
                    add(ASSOC)
                rest = _SENIOR_LECT.sub(' ', _ASSOC_LECT.sub(' ', piece))
                if _LECTURER.search(rest):
                    add(ASST)
                plain_prof = True
            else:
                add(TEACH)
            continue
        if system == 'british' and _READER.search(piece):
            add(ASSOC)
            continue
        if _BRITISH_TEACHING.search(piece) or _TEACHING_ROLE.search(piece):
            add(TEACH)
            continue
        if _RESEARCH_ROLE.search(piece):
            add(RESEARCH)

    if not out:
        if _CHAIR.search(title):
            add(FULL)
        elif _FACULTY.search(title) or not _NON_ACADEMIC.search(title):
            # a faculty post that names no rank is open to any rank,
            # unless the advert says it is a teaching post
            if _DESC_NTT.search(description) and not _DESC_TT.search(description):
                add(TEACH)
            else:
                add(*PROF_RANKS)
                plain_prof = True

    # A North American "Assistant Professor of X" whose advert says it is
    # non-tenure-track (and never tenure-track) is a teaching post. When the
    # advert mentions both -- often just describing the department's
    # faculty -- the title's rank stands.
    if plain_prof and system == 'north_american' and not _TENURE.search(title) \
            and _DESC_NTT.search(description) and not _DESC_TT.search(description):
        out = [v for v in out if v not in PROF_RANKS]
        add(TEACH)

    out = [v for v in ORDER if v in out]
    return out or ['Unclassified']


_NON_ACADEMIC = _rx(
    r'\b(?:technician|support\s+officer|administrator|coordinator|manager|analyst|specialist|'
    r'librarian|clerk|director|dean|developer|engineer)\b')
