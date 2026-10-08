"""
Job info scraper for school_id 1603 - St. Thomas University (Canada)
ATS platform: own website
Careers link: https://www.stu.ca/employment/

No bulk info adapter applies to this school -- fetch_detail(url) below
visits each posting page individually and is THIS SCHOOL'S OWN detail-page
logic, owned entirely by this file (mirrors how find_links() works in this
school's job_postings script). Edit it directly if St. Thomas University's posting pages
need something the default doesn't handle (a click to reveal full text, a
login wall, a non-obvious title element, etc.); nothing here affects any
other school's script.

Default: render the page, take the first heading (or <title>) as the job
title and the page's visible text as the description.

Reads posting URLs from school_id_1603_job_postings.checkpoint (this
school's job_postings run) and classifies each one (position_type,
job_term, department_or_school, area_key_words, deadline_of_application,
position_start_date, job_title_in_post). area_key_words combines a
rule-based primary keyword read off the title's own rank clause (e.g.
"Assistant Professor in X" -> "X") with supporting keywords -- by default
scored via local TF-IDF against this school's OTHER postings (no API
needed); pass use_llm=True below instead if you have ANTHROPIC_API_KEY
configured, for an LLM read of each description instead (higher quality,
not validated in the session that wrote this script -- no credentials
were available there).

Writes school_job_info/school_id_1603_job_info.csv. Checkpointed to
school_id_1603_job_info.checkpoint next to this script -- kill-and-resume,
per-posting granularity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import job_info_lib as jinfo

SCHOOL_ID = 1603
SCHOOL_NAME = 'St. Thomas University'
CAREERS_LINK = 'https://www.stu.ca/employment/'
ATS_PLATFORM = 'own website'
USE_LLM = False  # set True once you have ANTHROPIC_API_KEY configured

JOB_POSTINGS_CHECKPOINT = os.path.join(HERE, '..', 'school_job_posts_code', f'school_id_{SCHOOL_ID}_job_postings.checkpoint')
CHECKPOINT_PATH = os.path.join(HERE, f'school_id_{SCHOOL_ID}_job_info.checkpoint')


# www.stu.ca serves its certificate without the intermediates (Let's Encrypt
# YE1 -> Root YE, cross-signed by ISRG Root X2). Browsers fetch those via
# AIA; requests does not, so every PDF failed CERTIFICATE_VERIFY_FAILED.
# The two intermediates are added to certifi's bundle for this school only --
# verification stays on, and the chain still ends at a trusted root.
_INTERMEDIATES = ('http://ye1.i.lencr.org/', 'http://ye.i.lencr.org/')
_BUNDLE = None


def _ca_bundle():
    global _BUNDLE
    if _BUNDLE is None:
        import ssl, tempfile, certifi
        pems = [open(certifi.where()).read()]
        for aia in _INTERMEDIATES:
            pems.append(ssl.DER_cert_to_PEM_cert(jinfo.jlib.requests.get(aia, timeout=20).content))
        fd, path = tempfile.mkstemp(suffix='.pem')
        with os.fdopen(fd, 'w') as f:
            f.write('\n'.join(pems))
        _BUNDLE = path
    return _BUNDLE


def fetch_detail(url):
    """CUSTOMIZED: PDF ads on www.stu.ca, fetched with the completed
    certificate chain (see _ca_bundle)."""
    import io
    from pypdf import PdfReader
    r = jinfo.jlib.requests.get(url, headers={'User-Agent': jinfo.jlib.UA}, timeout=30, verify=_ca_bundle())
    if r.status_code != 200:
        raise RuntimeError(f'pdf fetch failed status={r.status_code}')
    text = '\n'.join((page.extract_text() or '') for page in PdfReader(io.BytesIO(r.content)).pages)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return jinfo._pick_best_title(lines[:20]), text


def main():
    result = jinfo.run_school_job_info(SCHOOL_ID, JOB_POSTINGS_CHECKPOINT, CHECKPOINT_PATH,
                                        fetch_detail_fn=fetch_detail, use_llm=USE_LLM)
    err = result.get('last_error', '')
    n_ok = sum(1 for r in result['rows'].values() if 'error' not in r)
    print(f"{SCHOOL_NAME} (id={SCHOOL_ID}): status={result['status']} "
          f"rows={n_ok}/{len(result['rows'])}" + (f" ERROR: {err}" if err else ''))
    jinfo.close_browser()


if __name__ == '__main__':
    main()
