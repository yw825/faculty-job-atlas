"""
Job postings scraper for school_id 1688 - Goethe University Frankfurt (Germany)
ATS platform: own website
Careers link: https://berufungsportal.uni-frankfurt.de/

CUSTOMIZED (confirmed live): this is a Vaadin single-page app (the
university's professorship appointment portal) that needs noticeably longer
than the generic default's 2-second render wait before "Available
Positions" actually appears -- confirmed live, a 2s wait showed only the
word "Online" (the page's own status widget), a 5s wait showed both real
postings. Each posting has an "Apply for this position" link
("application?procedure=<GUID>"), which doesn't contain any job-shaped
keyword the generic default's filter looks for; the parallel "Job Posting"
PDF link works too but the application link is the more stable identifier.

TUNED FIND_LINKS
Goethe University's appointment portal is a Vaadin app listing each open
professorship as a card with a "Job Posting" PDF and an "Apply" link. The
apply link, application?procedure=<GUID>, is the only stable per-call URL,
so that is stored. The title (e.g. "Professorship (W2) for Political
Science with focus on violence research") is only inside the PDF, whose
link is minted per session -- posting_pdf_text() reopens the portal and
downloads it in that same session; the info script uses it.

Writes school_job_posts/school_id_1688_job_posts.csv (school_id, post_link).
Checkpointed to school_id_1688_job_postings.checkpoint next to this script.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_postings_lib as lib

SCHOOL_ID = 1688
SCHOOL_NAME = 'Goethe University Frankfurt'
CAREERS_LINK = 'https://berufungsportal.uni-frankfurt.de/'
ATS_PLATFORM = 'own website'

CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_postings.checkpoint')

APPLICATION_RE = re.compile(r'application\?procedure=')


PROCEDURE_RE = re.compile(r'application\?procedure=([0-9A-F-]{36})', re.I)
POSTING_URL = 'https://berufungsportal.uni-frankfurt.de/application?procedure={}'


def _open_portal(page):
    page.goto(CAREERS_LINK, timeout=45000, wait_until='domcontentloaded')
    try:
        page.wait_for_selector('a[href*="application?procedure="]', timeout=30000)
    except Exception:
        pass


def find_links():
    b = lib.get_browser()
    page = b.new_page(user_agent=lib.UA, viewport={'width': 1400, 'height': 1000})
    try:
        _open_portal(page)
        html = page.content()
    finally:
        page.close()
    return [POSTING_URL.format(g.upper()) for g in dict.fromkeys(PROCEDURE_RE.findall(html))]


def posting_pdf_text(url):
    """(title, text) of one call's "Job Posting" PDF. Its link is a Vaadin
    resource minted per session, so it is found and downloaded in the same
    browser page that rendered the portal."""
    import io
    from pypdf import PdfReader
    guid = PROCEDURE_RE.search(url).group(1).upper()
    b = lib.get_browser()
    page = b.new_page(user_agent=lib.UA, viewport={'width': 1400, 'height': 1000})
    try:
        _open_portal(page)
        pdf_href = page.evaluate(
            """guid => {
                const apply = [...document.querySelectorAll('a[href*="application?procedure="]')]
                    .find(a => a.href.toUpperCase().includes(guid));
                let card = apply;
                for (let i = 0; card && i < 8; i++) {
                    card = card.parentElement;
                    const pdf = card && card.querySelector('a[href$=".pdf"]');
                    if (pdf) return pdf.href;
                }
                return null;
            }""", guid)
        if not pdf_href:
            raise RuntimeError('frankfurt: call no longer listed: ' + url)
        body = page.request.get(pdf_href).body()
    finally:
        page.close()
    reader = PdfReader(io.BytesIO(body))
    text = '\n'.join((p.extract_text() or '') for p in reader.pages)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    idx = next((i for i, l in enumerate(lines) if re.search(r'professor', l, re.I)), 0)
    title = lines[idx] if lines else ''
    # PDF lines wrap mid-title ("...with focus on violence" / "research (focus
    # on Global South)"): join continuation lines that start in lower case
    for nxt in lines[idx + 1:idx + 3]:
        if nxt[:1].islower() or nxt.startswith('('):
            title += ' ' + nxt
        else:
            break
    title = re.split(r'(?<=[a-z)])\.\s', title)[0]
    return title, re.sub(r'\s+', ' ', text)[:20000]


def main():
    result = lib.run_checkpointed(SCHOOL_ID, CHECKPOINT_PATH, find_links)
    err = result.get('last_error', '')
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"links={len(result['links'])}" + (f" ERROR: {err}" if err else ''))
    lib.close_browser()


if __name__ == '__main__':
    main()
