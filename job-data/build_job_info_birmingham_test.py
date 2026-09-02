"""
One-off test build of school_id_1763_job_info.csv (University of Birmingham),
per the user's explicit "let's apply to UK first and test out" scoping.

Classification below was done by reading each of Birmingham's 33 real scraped
postings (title + department + description text) directly -- not a keyword
script. position_type follows the agreed UK mapping:
  - Assistant Professor / Associate Professor / Professor (incl. "(Education)"
    variants, which are UK teaching-focused contract types, still map to the
    same US-style rank the school itself uses in the title) -> the matching
    Assistant_Professor / Associate_Professor / Full_Professor value.
  - "Teaching Fellow" (UK fixed-term teaching-only academic role, closest
    equivalent to Lecturer) -> Lecturer.
  - "Research Fellow" / "Research Associate" / postdoctoral research roles
    -> Research_Fellow (new 5th value, added this session per explicit user
    instruction: "let's add another value, which is Research Fellow. This
    value includes all research related positions such as post-doc").
  - "Assistant or Associate Professor" (posting spans both ranks) -> both
    values, per the user's explicit multi-value instruction.
  - Two postings ("In Vivo Microscopy Specialist Technician", "Research
    Technician") are pure lab/technical-support staff roles, not an academic
    or research-fellow role -> Non-academic (new 6th value, added this
    session per explicit user instruction: "some posts may also have
    non-academic position. We can add another value in position type,
    called Non-academic").

job_term: none of the 33 postings signal part-time/flexible-only; UK academic
postings default to full-time unless stated otherwise -> Full-time for all.

position_start_date: no posting states an actual position start date (two
mention a funded project's END date, which is not the same thing) -- left
blank rather than guessed.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_CSV = os.path.join(HERE, 'school_job_posts', 'school_id_1763_job_posts.csv')
OUT_CSV = os.path.join(HERE, 'school_job_posts', 'school_id_1763_job_info.csv')

FIELDS = ['school_id', 'posting_url', 'position_type', 'job_term',
          'department_or_school', 'area_key_words',
          'deadline_of_application', 'position_start_date']

# keyed by job id parsed out of posting_url (.../job/<id>)
CLASSIFICATION = {
    '9938': dict(position_type='Research_Fellow', dept='Department of Pharmacy',
                 keywords='nanomaterials; mitochondrial nucleic acid delivery', deadline='2026-09-23'),
    '9913': dict(position_type='Research_Fellow', dept='School of Metallurgy and Materials',
                 keywords='superalloys; materials science; nuclear/aerospace materials', deadline='2026-09-22'),
    '9919': dict(position_type='Research_Fellow', dept='Department of Applied Health Sciences',
                 keywords='maternal health; cardiometabolic risk; mixed methods research', deadline='2026-09-16'),
    '9918': dict(position_type='Research_Fellow', dept='Department of Applied Health Sciences',
                 keywords='maternal health; cardiometabolic risk; mixed methods research', deadline='2026-09-16'),
    '9923': dict(position_type='Research_Fellow', dept='Department of Immunology and Immunotherapy',
                 keywords='immunology; immunotherapy', deadline='2026-09-15'),
    '9910': dict(position_type='Assistant_Professor', dept='School of Mechanical Engineering',
                 keywords='robotics; artificial intelligence', deadline='2026-09-21'),
    '9920': dict(position_type='Research_Fellow', dept='Department of Immunology and Immunotherapy',
                 keywords='immunology; immunotherapy; research bids', deadline='2026-09-07'),
    '9922': dict(position_type='Research_Fellow', dept='Department of Immunology and Immunotherapy',
                 keywords='immunology; type 1 diabetes; murine models', deadline='2026-09-14'),
    '9842': dict(position_type='Research_Fellow', dept='School of Engineering',
                 keywords='bladder cancer; diagnostics; photonics', deadline='2026-09-17'),
    '9869': dict(position_type='Research_Fellow', dept='College of Arts and Law',
                 keywords='sign language; sociolinguistics; language evolution', deadline='2026-09-10'),
    '9889': dict(position_type='Research_Fellow', dept='School of Chemistry',
                 keywords='materials chemistry; electromagnetic attenuation', deadline='2026-09-17'),
    '9786': dict(position_type='Research_Fellow', dept='School of Psychology',
                 keywords='psychology; Horizon Trace project', deadline='2026-09-07'),
    '9878': dict(position_type='Research_Fellow', dept='School of Chemistry',
                 keywords='chemistry', deadline='2026-09-02'),
    '9771': dict(position_type=['Assistant_Professor', 'Associate_Professor'], dept='School of Engineering',
                 keywords='structural engineering', deadline='2026-10-12'),
    '9853': dict(position_type='Assistant_Professor', dept='Birmingham Business School',
                 keywords='finance; business education', deadline='2026-09-14'),
    '9886': dict(position_type='Full_Professor', dept='School of Mathematics',
                 keywords='statistics; data science', deadline='2026-09-20'),
    '9803': dict(position_type='Research_Fellow', dept='School of Chemistry',
                 keywords='chemical biology; nucleic acids', deadline='2026-09-13'),
    '9814': dict(position_type='Non-academic', dept='College of Medicine and Health',
                 keywords='biomedical imaging; microscopy; technical support', deadline='2026-10-04'),
    '9833': dict(position_type='Research_Fellow', dept='Department of Cardiovascular Sciences',
                 keywords='cardiovascular immunology; atherosclerosis', deadline='2026-09-13'),
    '9824': dict(position_type='Non-academic', dept='Department of Cancer and Genomic Sciences',
                 keywords='research technical support', deadline='2026-09-10'),
    '9863': dict(position_type='Associate_Professor', dept='Department of Pharmacy',
                 keywords='clinical pharmacy; pharmacy education', deadline='2026-09-15'),
    '9823': dict(position_type='Lecturer', dept='School of Psychology',
                 keywords='psychology; teaching', deadline='2026-09-13'),
    '9792': dict(position_type='Research_Fellow', dept='Applied Health Sciences',
                 keywords='breast cancer; health inequalities; qualitative research', deadline='2026-09-14'),
    '9796': dict(position_type='Assistant_Professor', dept='Department of Biomedical Sciences',
                 keywords='anatomy; medical education', deadline='2026-09-07'),
    '9813': dict(position_type='Research_Fellow', dept='Department of Immunology and Immunotherapy',
                 keywords='immunology; type 1 diabetes; NAMPT inhibitors', deadline='2026-09-07'),
    '9791': dict(position_type='Research_Fellow', dept='School of Sport, Exercise and Rehabilitation Sciences',
                 keywords='neuroscience; spinal cord injury; neuromodulation', deadline='2026-09-06'),
    '9800': dict(position_type='Lecturer', dept='School of Psychology',
                 keywords='psychology; teaching', deadline='2026-09-06'),
    '9809': dict(position_type='Research_Fellow', dept='School of Social Policy',
                 keywords='intellectual disabilities; mental health; clinical trial', deadline='2026-09-06'),
    '9810': dict(position_type='Research_Fellow', dept='School of Social Policy',
                 keywords='intellectual disabilities; social policy research', deadline='2026-09-06'),
    '9784': dict(position_type='Research_Fellow', dept='School of Computer Science',
                 keywords='robotics; machine learning; human-AI collaboration', deadline='2026-09-03'),
    '9766': dict(position_type='Research_Fellow', dept='School of Physics and Astronomy',
                 keywords='gravitational waves; astrophysics', deadline='2026-09-30'),
    '9765': dict(position_type='Research_Fellow', dept='School of Biosciences',
                 keywords='neuroscience; behavioural neuroscience; Drosophila', deadline='2026-09-15'),
    '9700': dict(position_type='Research_Fellow', dept='School of Chemistry',
                 keywords='computational materials; chemistry', deadline='2026-09-02'),
}


def main():
    rows_out = []
    with open(IN_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            job_id = row['posting_url'].rstrip('/').rsplit('/', 1)[-1]
            c = CLASSIFICATION.get(job_id)
            if c is None:
                continue
            pt = c['position_type']
            pt = pt if isinstance(pt, list) else [pt]
            rows_out.append({
                'school_id': row['school_id'],
                'posting_url': row['posting_url'],
                'position_type': '; '.join(pt),
                'job_term': 'Full-time',
                'department_or_school': c['dept'],
                'area_key_words': c['keywords'],
                'deadline_of_application': c['deadline'],
                'position_start_date': '',
            })

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f'wrote {len(rows_out)} rows to {OUT_CSV}')


if __name__ == '__main__':
    main()
