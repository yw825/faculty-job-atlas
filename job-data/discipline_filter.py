"""Which faculty postings the map shows: the user's own fields only.

The user's decision of 2026-10-22 ("I only care about jobs related to me"):
keep business analytics / information systems / MIS, data science /
operations research / industrial engineering, and statistics / applied
math -- drop postings that are clearly in some other field. This is a
first pass: it removes only what is UNAMBIGUOUSLY outside those fields
(a title/department/keyword match on medicine, nursing, humanities, pure
natural science, pure business functions, non-target engineering
branches, education, law, the arts, ...). A posting that names no
department this precise, or whose department could plausibly be one of
the three groups, is left on the map rather than guessed away -- the user
can prune further once this pass is reviewed.

Matching runs over title + department_or_school + area_key_words together,
since a school's own naming varies (department_or_school is often blank,
and the discipline then shows up only in the title or the keywords read
from the advert text).
"""
import re

# The three groups, and their close synonyms, as the user described them
# (2026-10-22): business analytics/IS/MIS; data science/OR/IE; stats/applied
# math. A match here always keeps the posting, even if NOT_RELEVANT also
# matches (e.g. "Assistant Professor of Finance and Business Analytics").
RELEVANT = re.compile(
    r"(?i)business\s+analytics|business\s+intelligence|"
    r"(?:management\s+)?information\s+systems?|\bMIS\b|decision\s+sciences?|"
    r"data\s+scien|operations?\s+research|\bORIE\b|"
    r"\bindustrial\b.{0,30}engineer|"
    r"biostatistics|\bstatistics\b|statistical|applied\s+math|computational\s+math|"
    r"quantitative\s+(?:methods|analysis|finance|biology|psychology)|"
    r"machine\s+learning|"
    r"predictive\s+analytics|data\s+analytics"
    # Deliberately NOT included: bare "artificial intelligence"/"AI" -- it
    # shows up as often in medicine, law and philosophy postings ("AI in
    # Medicine", "AI Ethics") as in the user's own fields, so it cannot
    # safely override a NOT_RELEVANT match the way "machine learning" or
    # "data science" can.
)

# Fields clearly outside the three groups. Grouped by area for review; each
# group lists a department/field name, not a job title, so "Professor of
# Biology" is caught by \bbiology\b in title or department text.
NOT_RELEVANT = re.compile(
    r"(?i)"
    # medicine / health / clinical (incl. the common subspecialty names --
    # a medical school's own listings are otherwise almost all ambiguous:
    # no RELEVANT or NOT_RELEVANT word, just a specialty name)
    r"\bmedicine\b|\bmedical\b|\bnursing\b|\bdental\b|dentistry|\bpharmacy\b|pharmacolog|"
    r"\bveterinary\b|physical\s+therapy|occupational\s+therapy|speech[- ](?:language\s+)?patholog|"
    r"\baudiology\b|\bradiolog|\bnutrition\b|\bdietetics\b|\bkinesiology\b|exercise\s+science|"
    r"athletic\s+training|\bpublic\s+health\b|\bepidemiology\b|anesthesiolog|\bcardiolog|"
    r"\boncology\b|\bneurology\b|neurosurg|neuroscience|\bpsychiatry\b|obstetrics|gynecolog|\bpediatrics\b|"
    r"\bsurgery\b|\boptometry\b|\bpodiatry\b|clinical\s+(?:education|psychology)|\bdermatolog|"
    r"\bimmunology\b|\bpathology\b|\bphysiology\b|\banatomy\b|\bgenetics\b|\bmicrobiology\b|"
    r"\bbiochemistry\b|\btoxicology\b|respiratory\s+(?:therapy|care)|\bparamedic\b|\bmidwifery\b|"
    r"\burology\b|urologist|endourolog|ophthalmolog|otolaryngolog|gastroenterolog|nephrolog|"
    r"rheumatolog|\bhematolog|pulmonolog|hepatolog|\borthop(?:a)?edic|geriatrics|palliative\s+care|"
    r"allergy\s+and\s+immunology|emergency\s+medicine|family\s+medicine|internal\s+medicine|"
    r"\bphysician\b|neuropatholog|infectious\s+disease|endocrinolog|neonatolog|\bdiabetes\b|"
    r"heart\s+disease|cardiovascular|academic\s+clinician\s+track|clinician[- ]educator|"
    r"\bperinatal\b|violence\s+prevention|"
    # humanities / languages / arts
    r"\benglish\b|literature|\bhistory\b|\bphilosophy\b|\breligion\b|religious\s+studies|theolog|"
    r"linguistics|\bclassics\b|\bLatin\b|ancient\s+Greek|foreign\s+languages?|modern\s+languages?|"
    r"\bSpanish\b|\bFrench\b|\bGerman\b|\bItalian\b|\bChinese\b|\bJapanese\b|\bRussian\b|\bArabic\b|"
    r"\bart\s+(?:history|education)\b|\bfine\s+arts\b|\bstudio\s+art\b|\bmusic\b|\btheatre\b|\btheater\b|"
    r"\bdance\b|graphic\s+design|\bfilm\b|\bcinema\b|photography|creative\s+writing|\bhumanities\b|"
    # social sciences (non-quantitative)
    r"\bsociology\b|\banthropology\b|political\s+science|\bpsychology\b|social\s+work|"
    r"criminal\s+justice|criminology|\bjournalism\b|\bcommunication(?:s)?\b(?!.{0,30}(?:information\s+systems|analytics))|"
    r"public\s+administration|international\s+relations|gender\s+studies|women'?s\s+studies|"
    r"ethnic\s+studies|\bcounsel(?:ing|or|ling)\b|"
    r"\beconomics\b(?!.{0,30}(?:quantitative|econometric|data))|"
    # education / library
    r"\beducation\b(?!al\s+(?:data|technology))|curriculum\s+and\s+instruction|"
    r"educational\s+leadership|teacher\s+education|early\s+childhood|special\s+education|"
    r"library\s+science|\blibrarian\b|"
    # pure natural / earth sciences
    r"\bbiology\b|\bchemistry\b|\bphysics\b(?!.{0,30}(?:computational|data))|\bgeology\b|"
    r"\bgeography\b|environmental\s+science|earth\s+science|\bastronomy\b|\becology\b|"
    r"marine\s+(?:science|biology)|\bagricultur|agronomy|animal\s+science|horticulture|"
    r"\bbotany\b|\bzoology\b|\bentomology\b|\bforestry\b|"
    # law
    r"\blaw\b|legal\s+studies|\bparalegal\b|\bjurisprudence\b|"
    # pure business functions (not analytics/IS/MIS)
    r"\baccounting\b|\bfinance\b(?!.{0,30}quantitative)|\bmarketing\b|\bmanagement\b(?!.{0,30}information)|"
    r"entrepreneurship|human\s+resources|organizational\s+behavior|hospitality|"
    # computer science / electrical & computer engineering, unqualified --
    # the user's engineering group is data science / OR / IE specifically,
    # not CS or ECE generally; RELEVANT above still rescues a posting that
    # also names data science, ML, AI or analytics.
    r"computer\s+science\b|computer\s+engineering|electrical\b.{0,30}engineering|"
    r"\bcybersecurity\b|information\s+technology\b(?!.{0,20}(?:analytics|data))|"
    # non-target engineering branches -- department names routinely read
    # "X and Engineering" or "X Science and Engineering" (Nuclear Science
    # and Engineering, Materials Science and Engineering, Civil and
    # Environmental Engineering), so a short gap is allowed before "engineer"
    r"\bcivil\b.{0,25}engineer|\bmechanical\b.{0,25}engineer|aero(?:space|astro)\b.{0,25}engineer|"
    r"\bchemical\b.{0,25}engineer|\bbiomedical\b.{0,25}engineer|bioengineer|biological\s+engineer|"
    r"\bmaterials\b.{0,25}engineer|\benvironmental\b.{0,25}engineer|\bnuclear\b.{0,25}engineer|"
    r"\bconstruction\b.{0,25}(?:management|engineer)|\bpetroleum\b.{0,25}engineer|\bmining\b.{0,25}engineer|"
    r"\bagricultural\b.{0,25}engineer|"
    # misc
    r"\barchitecture\b|\bculinary\b|\bathletics\b|\bcoaching\b|\btheology\b"
)


def is_relevant(title, department='', keywords=''):
    text = ' '.join(filter(None, (title, department, keywords)))
    if not text.strip():
        return True  # nothing to judge by -- don't guess it away
    if RELEVANT.search(text):
        return True
    if NOT_RELEVANT.search(text):
        return False
    return True  # ambiguous: leave it for a later, closer pass
