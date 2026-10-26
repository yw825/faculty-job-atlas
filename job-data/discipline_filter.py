"""Which faculty postings the map shows: the user's own fields only.

The user's fields (2026-10-22): business analytics / information systems /
MIS; data science / operations research / industrial engineering;
statistics / applied math; and AI / machine learning. Everything else is
dropped -- the fields are narrow, so an ambiguous posting is dropped too.

The decision reads the posting's own words in order of trust:
  1. HARD_EXCLUDE anywhere in title or department -> drop. Fields the user
     named one by one as not theirs, even with AI or data in the title.
  2. The title. It names the job's own field, so it decides whenever it
     names one: a narrow core term (statistics, biostatistics, OR, IE, IS,
     business analytics, applied math) -> keep, whatever else it names;
     a broader core term (AI, ML, data science) and no other field -> keep; another field and
     no core field -> drop; both ("AI in Biology") -> the department breaks
     the tie. Health/clinical and computer-science words don't count as
     "another field" next to a core term in a title -- the user wants AI in
     healthcare, and "Computer Science (AI)" is an AI job.
  3. The department, when the title names no field ("Assistant
     Professor"): core only -> keep; another field -> drop.
  4. The advert keywords, only when title and department are both silent
     or mixed -- and only the narrow terms (operations research, business
     analytics, ...). Broad words like "AI", "statistical" or "data
     science" turn up in nearly every advert and don't count here.
"""
import re

CORE = re.compile(
    r"(?i)business\s+analytics|business\s+intelligence|decision\s+analytics|"
    r"(?<!geographic\s)(?<!geographical\s)(?:management\s+)?information\s+systems?|"
    r"\bMIS\b(?!\s*\(masters\s+in\s+simulation)|"
    r"decision\s+sciences?|management\s+science|"
    r"data\s+scien|data\s+mining|data\s+analytics|predictive\s+analytics|"
    r"operations?\s+research|operations?\s+management|\bORIE\b|optimi[sz]ation|"
    r"\bindustrial\b.{0,30}engineer|\bindustrial\s+eng\b|"
    r"biostatistic|\bstatistics\b|"
    r"\bstatistical\s+(?:science|learning|methods|modeling|programming|computing|inference|consulting)|"
    r"applied\s+math|computational\s+math|"
    r"machine\s+learning|deep\s+learning|artificial\s+intelligence|\bAI\b|\bAI/ML\b"
)

# Narrow terms that are trusted even when only the advert keywords say
# them -- each one names the user's field and little else.
CORE_NARROW = re.compile(
    r"(?i)business\s+analytics|"
    r"(?<!geographic\s)(?<!geographical\s)(?<!quantum\s)information\s+systems|"
    r"\bMIS\b(?!\s*\(masters\s+in\s+simulation)|decision\s+sciences?|management\s+science|"
    r"operations\s+research|"
    r"\bindustrial\b.{0,30}engineer|biostatistic|applied\s+math"
)

# A title naming one of these is the user's job whatever else it names
# ("Biostatistics and Bioinformatics", "Industrial Engineering
# (Manufacturing Systems)", "Introductory Statistics in Psychology").
TITLE_STRONG = re.compile(
    CORE_NARROW.pattern + r"|\bstatistics\b|business\s+intelligence|\bindustrial\s+eng\b")

# Fields the user named as not theirs (2026-10-22, 2026-10-26), dropped
# even when the posting also names AI, data science or statistics.
HARD_EXCLUDE = re.compile(
    r"(?i)electrical|electronic|computer\s+engineering|\bcomputer\s+engr|\bECE\b|"
    r"\beconomics?\b|economic\s+science|construction\s+management|\bmarketing\b|"
    r"chemi(?:stry|cal)|biochem|\bchem(?:be)?\b|catalys|geolog|geoscien|geophysic|politic|"
    r"robotic|embodied\s+AI|"
    r"supply\s+chain|\blogistics\b"
)

# Health and clinical fields: another field when they stand alone, but
# not when the title also names a core field ("AI in Healthcare" stays).
HEALTH = re.compile(
    r"(?i)\bmedicine\b|\bmedical\b|\bnursing\b|\bdental\b|dentistry|\boral\s+health|craniofacial|"
    r"orofacial|orthodontic|\bpharmacy\b|pharmacolog|behavioral\s+health|biobehavioral|"
    r"\bmental\s+health\b|substance\s+(?:use|abuse)\b|\bhealth\b|"
    r"\bveterinary\b|physical\s+therapy|occupational\s+therapy|speech[- ](?:language\s+)?patholog|"
    r"\baudiology\b|\bradiolog|\bnutrition\b|\bdietetics\b|\bkinesiology\b|exercise\s+science|"
    r"athletic\s+training|\bepidemiolog|anesthesiolog|\bcardiolog|"
    r"\boncology\b|\bcancer\b|\bneurology\b|neurosurg|\bpsychiatr|obstetrics|gynecolog|\bpediatric|"
    r"\bsurgery\b|\boptometry\b|\bpodiatry\b|\bdermatolog|"
    r"\bimmunology\b|\bpathology\b|\btoxicology\b|respiratory\s+(?:therapy|care)|\bparamedic\b|\bmidwifery\b|"
    r"\burology\b|urologist|endourolog|ophthalmolog|otolaryngolog|gastroenterolog|nephrolog|"
    r"rheumatolog|\bhematolog|pulmonolog|hepatolog|\borthop(?:a)?edic|geriatrics|palliative\s+care|"
    r"\bphysician\b|neuropatholog|infectious\s+disease|endocrinolog|neonatolog|\bdiabetes\b|"
    r"heart\s+disease|cardiovascular|clinician|\bperinatal\b|violence\s+prevention|"
    r"\bdrug\s+discovery|occupational\s+medicine"
)

# Computer science: another field on its own (a plain CS job isn't the
# user's), but not next to a core term in a title ("Computer Science --
# Artificial Intelligence" is an AI job).
COMPUTING = re.compile(
    r"(?i)computer\s+science|\bcomputing\b|computer\s+(?:and\s+)?information\s+science|"
    r"software\s+engineer|\bcyber|information\s+technology|human[- ]computer|\bHCI\b"
)

# Every other field.
OTHER = re.compile(
    r"(?i)"
    # engineering branches outside data science / OR / IE
    r"\bcivil\b|\bmechanical\b|mechatronic|aero(?:space|nautic|astro)|astronautic|"
    r"bio(?:medical|logical)\s+engineer|bioengineer|\bmaterials\b|\bnuclear\b|"
    r"\benvironmental\s+engineer|\bpetroleum\b|\bmining\b|\bagricultural\b|"
    r"semiconductor|\benergy\b|\bpower\s+systems|"
    r"engineering\s+technology|geospatial|"
    # natural and earth sciences
    r"\bphysics\b|physical\s+sciences?|astrophysic|\bastronom|\bquantum\b|biophysic|"
    r"\bbiolog|\becolog|evolution|\bgenetic|genomic|\bomics\b|proteomic|\bmolecular\b|\bcell\b|"
    r"neuroscien|neuroAI|\bneuro|cognitive|\bbrain\b|physiolog|\banatomy\b|microbiolog|"
    r"\bgeograph|environmental\s+(?:science|studies)|earth\s+science|\bocean|\bclimate\b|"
    r"atmospher|\bmarine\b|\bagricultur|agronomy|animal\s+science|horticulture|"
    r"\bbotany\b|\bzoology\b|\bentomology\b|\bforestry\b|\bwater\b|\bfluid\b|\bplasma\b|"
    r"synthetic\s+biology|nanobio|\btowing\b|\bmaterials?\b|life\s+sciences?|bioscience|"
    r"bioinformatic|\benvironment|\bcrops?\b|microbiom|\bengines?\b|\bpower\b(?!\s+analysis)|"
    r"networking|infrastructure|construction|architect|"
    # social sciences, education, law
    r"\bpsycholog|psychometric|\bsociolog|\banthropolog|social\s+work|social\s+science|"
    r"socioeconomic|criminal\s+justice|criminology|\bjournalism\b|\bcommunication|\bmedia\b|"
    r"public\s+(?:administration|policy)|international\s+relations|\bgovernment\b|"
    r"gender|women'?s\s+studies|sexuality|ethnic\s+studies|african\s+american|\bcounsel(?:ing|or|ling)\b|"
    r"\beducation|learning\s+sciences|curriculum|teacher\s+(?:education|preparation)|early\s+childhood|"
    r"librar|\bLIS\b|\bwriting\b|copyright|\blaw\b|lawyering|legal|\bparalegal\b|jurisprudence|"
    # humanities and arts
    r"\benglish\b|literature|\bhistory\b|\bphilosophy\b|\bethic|\breligio|theolog|"
    r"linguistic|\bclassics\b|(?<!natural\s)\blanguages?\b(?!\s+(?:models?|processing))|\bSpanish\b|\bFrench\b|\bGerman\b|\bItalian\b|"
    r"\bChinese\b|\bJapanese\b|\bRussian\b|\bArabic\b|\bfine\s+arts\b|\bstudio\s+art\b|"
    r"\bart\s+(?:history|education)\b|\bmusic\b|\baudio\b|\btheat(?:re|er)\b|\bdance\b|\bdrama\b|"
    r"\bacting\b(?!\s+(?:assistant|associate|professor|instructor|chair|director|dean|head))|"
    r"\bdesign\b|\bfilm\b|\bcinema\b|photography|creative|\bhumanities\b|visual|performance|"
    # business functions outside analytics / IS / OR
    r"\baccounting\b|accountancy|\bfinance\b|entrepreneur|human\s+resources|"
    r"organizational\s+behavior|hospitality|\btourism\b|\bsport|"
    # misc
    r"\barchitecture\b|\bculinary\b|\bathletics\b|\bcoaching\b"
)


def _other(text, lenient):
    if OTHER.search(text):
        return True
    return not lenient and bool(HEALTH.search(text) or COMPUTING.search(text))


def is_relevant(title, department='', keywords=''):
    title = title or ''
    department = department or ''
    keywords = keywords or ''
    if not (title + department + keywords).strip():
        return True  # truly nothing to judge by
    if HARD_EXCLUDE.search(title) or HARD_EXCLUDE.search(department):
        return False
    if TITLE_STRONG.search(title):
        return True
    # "Department of Statistics in the College of Literature, Science, and
    # the Arts": only the department itself, not its parent college.
    department = re.split(r"(?i)\s+(?:in|within)\s+the\s+", department, 1)[0]

    dept_core = bool(CORE.search(department))
    dept_other = _other(department, lenient=False)

    if CORE.search(title):
        if not _other(title, lenient=True):
            return True
        return dept_core and not dept_other
    if _other(title, lenient=False):
        return False

    if dept_core and not dept_other:
        return True
    if dept_other and not dept_core:
        return False
    return bool(CORE_NARROW.search(keywords)) and not HARD_EXCLUDE.search(keywords)


# The map's subject areas, in display order. Each posting is filed under the
# subjects its title names; if the title names none, its department's; if
# neither does, its advert keywords'. The page uses these both for the
# "Subject area" filter and for the card title ("Assistant Professor of
# Statistics"), so the two always agree.
SUBJECTS = [
    ('Business Analytics', re.compile(
        r"(?i)business\s+analytics|business\s+intelligence|decision\s+analytics|"
        r"data\s+analytics|predictive\s+analytics|\banalytics\b")),
    ('Information Systems', re.compile(
        r"(?i)(?<!geographic\s)(?<!geographical\s)(?<!quantum\s)information\s+systems?|"
        r"\bMIS\b(?!\s*\(masters\s+in\s+simulation)|\bCIS\b")),
    ('Data Science', re.compile(r"(?i)data\s+scien|data\s+mining")),
    ('AI & Machine Learning', re.compile(
        r"(?i)artificial\s+intelligence|\bAI\b|machine\s+learning|deep\s+learning|"
        r"natural\s+language\s+processing|\bNLP\b|large\s+language\s+models?|\bLLMs?\b")),
    ('Operations Research', re.compile(
        r"(?i)operations?\s+research|operations?\s+management|management\s+science|"
        r"decision\s+sciences?|optimi[sz]ation|\bORIE\b|stochastic")),
    ('Industrial Engineering', re.compile(
        r"(?i)\bindustrial\b.{0,30}engineer|\bindustrial\s+eng\b|\bISE\b")),
    ('Statistics', re.compile(r"(?i)statistic|econometric|probabilit")),
    ('Mathematics', re.compile(r"(?i)mathemat|applied\s+math|computational\s+math|\bmath\b")),
]


def subjects_of(title, department='', keywords=''):
    """Names of the SUBJECTS this posting is filed under (possibly several,
    possibly none), from the most specific text that names any."""
    department = re.split(r"(?i)\s+(?:in|within)\s+the\s+", department or '', 1)[0]
    for text in (title or '', department, keywords or ''):
        found = [name for name, rx in SUBJECTS if rx.search(text)]
        if found:
            return found
    return []
