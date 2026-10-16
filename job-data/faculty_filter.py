"""Which postings the map shows: faculty jobs and postdocs only.

The user's decision of 2026-10-14 ("I only want faculty jobs"): keep
professor / lecturer / instructor / adjunct / clinical faculty, deans and
chairs, faculty librarians, postdocs and research fellows; drop staff,
coaches, student jobs and PhD studentships. Boards that mix staff and
faculty jobs are cut down here even when their link has no faculty filter.

The job title decides. The info stage's rank (read from the advert text)
only rescues a title that names no job at all and contains no staff word.
Measured on the 29,519 postings of the 699 audited schools: 15.6k kept.
"""
import re
# Faculty + postdocs (user's choice, 2026-10-14). The title decides; the info
# stage's rank (read from the advert text) only rescues a title that names
# no job ("Biology - Assistant"?) and contains no staff word.
EXCLUDE = re.compile(r"(?i)(?:^student\b|^\(S\)\s|\bstudent\s*[-–]\s|\bstudent (?:assistant|worker|employee|employment|hire|job|position|ambassador|intern|office|support|staff|clerk|aide|helper|tutor|technician|lab|leader|manager|coordinator|services? (?:assistant|worker))|studerende|studentermedhj|studentmedarbe|work[ -]?study|\bFWS\b|graduate (?:teaching |research )?assistant|\bG\.?A\.?\s*[-–(]|teaching assistant|\bTA[_ ]|\bcupe|\bintern(?:ship)?s?\b|\bcoach|ph\.?\s?d\.?\s*(?:student|candidate|position|scholarship|studentship|fellowship|project|researcher|programme|program)|\bphd\b|(?<![Pp]ost)(?<![Pp]ost-)doctoral (?:candidate|student|researcher|position|scholarship|network)|doktorand|doctorant|promovend|predoc|pre-doc|stipendiat|research assistant\b(?! professor| prof)|lab(?:oratory)? (?:assistant|technician|manager)|casual hire|volunteer|(?:group fitness|fitness|swim(?:ming)?|yoga|pilates|aquatics?|(?:water )?aerobics|lifeguard|cpr|first aid|driving|ski|climbing|zumba|spin|cycling|exercise class)[\w ]{0,20}instructor|faculty (?:administrative|support|affairs|services|staff|development coordinator|coordinator|executive)|workday is currently unavailable|employment opportunities$)")
STRONG = re.compile(r"(?i)(?:professor|profesor|professeur|professore|professur|\bprof\.|hoogleraar|\bdocent|\blektor|lecturer|\breader\b|\badjunct|\badjunkt|teaching (?:fellow|professor|faculty|position|scholar)|\bdean\b|department (?:head|chair)|endowed|post-?doc|postdoktor|post-doctoral|research fellow|clinical fellow|research associate\b|librarian|maître de conférences|maitre de conferences|enseignant|ricercatore|\bRTD\b|catedr|tenure|\bW[123]\b|juniorprof|research professor|\bAPTPUO\b|ramón y cajal|marie (?:skłodowska-)?curie|universitetslektor|faculté|教師|教授|講師|讲师|博士後|博士后|教職|教学科研|\bacademic \w*(?:ist|ian|ians|ists)\b|instructional faculty|clinical faculty|faculty associate|open rank|academic faculty|\bfaculty\b(?!\s*(?:support|affairs|administrative|services|staff|assistant\b(?! or)|coordinator|development|relations|liaison|executive|success|engagement|data|records|senate|club|housing|center|centre|grants?|payroll|recruit)))")
WEAK = re.compile(r"(?i)(?:^(?:department|school|faculty|college|division) of\b|visiting (?:researcher|scholar)|instructor|faculty|\bfellow(?:ship)?s?\b|\bchair\b(?! person| of the board)|scientist|clinician|attending|teacher|lærer|tutor\b|educator|preceptor)")
STAFF = re.compile(r"(?i)\b(?:coordinator|manager|specialist|administrator|administrative|assistant(?! (?:or associate )?professor| prof| teaching professor| dean| director of)|officer|technician|technologist|machinist|custodian|accountant|analyst|advisor|adviser|counselor|counsellor|clerk|driver|engineer\b|nurse\b|director(?! of (?:the )?(?:school|program|graduate|clinical education|academic|undergraduate))|secretary|receptionist|representative|cashier|cook|groundskeeper|mechanic|electrician|plumber|carpenter|painter|guard|police|security|recruiter|(?:hr|human resources) generalist|developer|designer|editor|writer|planner|buyer|controller|auditor|payroll|bookkeeper|housekeep|maintenance|dispatcher|operator|therapist|pharmacist|attorney|paralegal|chef|barista|server|lifeguard|attendant|aide\b|associate\b(?! (?:or full |\/full |\/ |)professor| dean| director| prof| instructor| lecturer)|supervisor|steward|usher|\bRN\b|registered nurse|\bLPN\b|\bCNA\b|tech\b|programmer|scheduler|navigator|liaison|consultant|executive\b|vice president|president\b|registrar|bursar|treasurer)")
FAC_RANKS = {'Assistant_Professor', 'Associate_Professor', 'Full_Professor', 'Lecturer', 'Research_Fellow'}

# A professor / lecturer / postdoc title is faculty whatever else it says
# ("Teaching Assistant Professor", "Assistant Professor and Coordinator of
# Graduate Internships", "Postdoctoral Research Assistant").
CORE = re.compile(r"(?i)professor|lecturer|\badjunct|post-?doc|postdoktor|post-doctoral|hoogleraar|maître de conférences|professeur|profesor\b|professur")


# Schools whose careers link lists faculty openings ONLY but whose postings
# carry titles the rules cannot read: UCLouvain's course-vacancy lists
# ("Faculté de droit et de criminologie"), the Québec universities'
# professor-call pages ("2026-11",
# "Offre d'emploi") and RWTH's professorship page. Everything there that is
# not explicitly excluded is kept. The Minnesota State universities' links
# select the IFO (Inter Faculty Organization) bargaining unit, so every job
# on them is a faculty appointment ("Clinical Education Director - Athletic
# Training Program" at Moorhead).
FACULTY_ONLY_BOARDS = {1639, 1650, 1665, 1684, 666, 674, 675, 683, 688, 694}


def is_faculty(title, ranks=(), school_id=None):
    t = (title or '').strip()
    if not t:
        return False
    if school_id in FACULTY_ONLY_BOARDS:
        return not EXCLUDE.search(t)
    if CORE.search(t) and not re.search(r'(?i)\bph\.?d\.?[- ]?(?:student|candidate|studentship|position)\b(?!.*post)', t):
        return True
    if EXCLUDE.search(t):
        return False
    if STRONG.search(t):
        return True
    if WEAK.search(t):
        return not STAFF.search(t)
    return bool(FAC_RANKS & set(ranks or ())) and not STAFF.search(t)
