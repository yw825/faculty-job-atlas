"""H-1B sponsorship stated in a US job advert.

posting_visa_status(advert) -> (status, sentence)

    'yes'      the advert says the school sponsors (or will consider
               sponsoring) H-1B / employment visas for this post
    'limited'  only for candidates already in the US (a change of status),
               "may not be available", or not for candidates subject to the
               $100,000 fee on new petitions (Presidential Proclamation of
               September 19, 2025)
    'no'       the advert says it will not sponsor, or that applicants must
               not need sponsorship now or in future
    ''         the advert says nothing either way

Generic I-9 lines ("must be authorized to work in the United States",
"employment is contingent on verification of work authorization") are not
a sponsorship statement -- every US employer has to say that -- and
"sponsored research", "employer sponsored plans" are not about visas.
"""
import re

_SENT = re.compile(r'[^.;!?\n]*(?:visa|h-?1-?b|sponsor|work\s+authori[sz]ation|authori[sz]ed\s+to\s+work)'
                   r'[^.;!?\n]*', re.I)
_VISA_CONTEXT = re.compile(r'(?i)\bvisa|\bh-?1-?b\b|\bimmigra|\bwork\s+(?:authori[sz]ation|permit)|'
                           r'\bemployment\s+authori[sz]ation|\bauthori[sz]ed\s+to\s+work|\bnonimmigrant|'
                           r'\bpermanent\s+residen|\bgreen\s+card|\bwork\s+status')
_NOT_VISA = re.compile(r'(?i)\w*[- ]?sponsored\s+(?:research|programs?|projects?|plans?|benefits?|by\s+the)|'
                       r'externally\s+sponsored|employer[- ]sponsored|sponsoring\s+(?:internships|events|student)|'
                       r'research\s+sponsors?|\bsponsors?\s+of\s+|industry\s+sponsor|other\s+sponsors|'
                       r'sponsor\s+(?:logistical|relocation|travel|moving)')
# "sponsor" counts only as visa sponsorship: the noun, or the verb with a
# visa, petition or person as its object.
_SPONSOR_VISA = re.compile(r'(?i)\bsponsorship\b|\bsponsor(?:s|ed|ing)?\s+(?:[\w-]+\s+){0,3}?'
                           r'(?:visas?|h-?1-?b|petitions?|applicants?|candidates?|individuals?|scholars?|'
                           r'faculty|employees?|international|foreign|nonresidents?|permanent|green)')
# Application-form questions ask the candidate; they say nothing about policy.
_QUESTION = re.compile(r'(?i)\b(?:are|do|will|would|can|have)\s+you\b|\bopen\s+ended\s+question')

_LIMITED = re.compile(
    r'(?i)may\s+not\s+be\s+available|'
    r'(?:already|currently)\s+(?:be\s+)?(?:in|inside|within)\s+the\s+(?:united\s+states|u\.?s\.?)|'
    r'change\s+(?:of|their)\s+(?:status|employer)|already\s+hold|currently\s+hold|'
    r'subject\s+to\s+the\s+\$?100,?000|\$100,?000\s+fee|presidential\s+proclamation|'
    r'outside\s+the\s+(?:united\s+states|u\.?s)|new\s+visa\s+sponsorship|initiate\s+sponsorship|'
    r'case[- ]by[- ]case|depend(?:s|ing)?\s+on|cannot\s+guarantee|not\s+guarantee|'
    r'\bnew\s+sponsorship|consular\s+processing|staff\s+positions')
_NO = re.compile(
    r'(?i)\b(?:not|unable|no\s+longer)\s+(?:be\s+)?(?:able\s+to\s+)?(?:[\w-]+\s+){0,3}?sponsor|'
    r'\bwill\s+not\s+(?:\w+\s+){0,2}?sponsor|\bdoes\s+not\s+(?:\w+\s+){0,2}?sponsor|\bcannot\s+sponsor|'
    r'\bnot\s+(?:a\s+)?sponsoring\s+agent|\bnot\s+(?:eligible\s+for|offer(?:ing)?|provide|available\s+for)\s+'
    r'(?:\w+\s+){0,2}?(?:visa|h-?1-?b|sponsorship)|\bsponsorship\s+(?:is\s+)?not\s+(?:available|offered|provided|possible)|'
    r'\bno\s+(?:visa|h-?1-?b|immigration)\s+sponsorship|\bwithout\s+(?:the\s+)?(?:need\s+for\s+)?'
    r'(?:current\s+or\s+future\s+)?(?:employer\s+|visa\s+)?sponsorship|'
    r'\b(?:need|require)\s+(?:visa\s+)?sponsorship[^.]{0,80}(?:not|ineligible|do\s+not\s+meet)|'
    r'\bmakes?\s+no\s+(?:implicit\s+)?(?:promise|commitment)s?\b|\bno\s+promises?\b')
_YES = re.compile(
    r'(?i)\b(?:will|is\s+able\s+to|are\s+able\s+to|able\s+to\s+consider|willing\s+to|may|can)\s+'
    r'(?:\w+\s+){0,2}?sponsor|\bsponsors\s+(?:[\w-]+\s+){0,3}?(?:visas?|h-?1-?b)|'
    r'\b(?:visa|h-?1-?b)\s+sponsorship\s+(?:is\s+)?(?:available|provided|offered|possible)|'
    r'\beligible\s+for\s+(?:visa|h-?1-?b)\s+sponsorship|\bconsider\s+sponsoring')


# Statements that rule sponsorship out without saying "visa" or "sponsor":
# UMGC's "Applicants must have and maintain their own legal status in the
# country where they apply to teach".
_OWN_STATUS = re.compile(
    r"(?i)\bmust\s+(?:have|hold|possess|maintain)\s+(?:and\s+maintain\s+)?(?:their|his\s+or\s+her|your)\s+own\s+"
    r"(?:legal|immigration|work|employment)\s+(?:status|authori[sz]ation)")


def posting_visa_status(advert):
    """('yes'|'limited'|'no'|'', the sentence it was read from)."""
    found = {}
    m = _OWN_STATUS.search(advert or '')
    if m:
        a = max(0, (advert or '').rfind('.', 0, m.start()) + 1)
        found['no'] = re.sub(r'\s+', ' ', advert[a:m.end() + 80]).strip()
    for m in _SENT.finditer(advert or ''):
        s = re.sub(r'\s+', ' ', m.group(0)).strip()
        s = _NOT_VISA.sub(' ', s)
        asked = advert[m.end():m.end() + 1] == '?'
        if len(s) > 600 or asked or _QUESTION.search(s):
            continue
        # bare "authorized to work" is I-9 boilerplate, and a bare "visa"
        # can be about benefits ("not available to holders of F1 or J1 visas")
        if not (_SPONSOR_VISA.search(s) or re.search(r'(?i)h-?1-?b', s)):
            continue
        if not (_VISA_CONTEXT.search(s) or _SPONSOR_VISA.search(s)):
            continue
        # keep the part of a run-on fragment that holds the statement
        k = re.search(r'(?i)visa|h-?1-?b|sponsor', s)
        s = s[max(0, k.start() - 160):].lstrip(' ,') if k else s
        if _NO.search(s) and _LIMITED.search(s):
            found.setdefault('limited', s)
        elif _NO.search(s):
            found.setdefault('no', s)
        elif _LIMITED.search(s):
            found.setdefault('limited', s)
        elif _YES.search(s):
            found.setdefault('yes', s)
    # A post that both offers sponsorship and limits it ("able to consider
    # sponsoring tenure-track ... not applicants subject to the fee") is
    # limited; a flat refusal outranks a general "the university sponsors".
    for status in ('limited', 'no', 'yes'):
        if status in found:
            if status == 'no' and 'yes' in found:
                return 'limited', found['no']
            return status, found[status]
    return '', ''
