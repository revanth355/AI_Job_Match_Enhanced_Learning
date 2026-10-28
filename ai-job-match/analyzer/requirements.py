"""Evidence-based checks of user-configured JD requirements, not hiring decisions."""
import math
import re
import unicodedata
from datetime import date


DEGREES = {
    "B.Tech": ("bachelor", r"(?i:\bb[.\s]*tech\b|\bbachelor(?:'s)? of technology\b)"),
    "B.E.": ("bachelor", r"\bB\.?\s?E\b\.?|(?i:\bbachelor(?:'s)? of engineering\b)"),
    "B.Sc": ("bachelor", r"(?i:\bb[.\s]*sc\b|\bbachelor(?:'s)? of science\b)"),
    "BCA": ("bachelor", r"(?i:\bbca\b|\bbachelor(?:'s)? of computer applications?\b)"),
    "B.Com": ("bachelor", r"(?i:\bb[.\s]*com\b|\bbachelor(?:'s)? of commerce\b)"),
    "B.A.": ("bachelor", r"\bB\.?\s?A\b\.?|(?i:\bbachelor(?:'s)? of arts\b)"),
    "M.Tech": ("master", r"(?i:\bm[.\s]*tech\b|\bmaster(?:'s)? of technology\b)"),
    "M.E.": ("master", r"\bM\.?\s?E\b\.?|(?i:\bmaster(?:'s)? of engineering\b)"),
    "M.Sc": ("master", r"(?i:\bm[.\s]*sc\b|\bmaster(?:'s)? of science\b)"),
    "MCA": ("master", r"(?i:\bmca\b|\bmaster(?:'s)? of computer applications?\b)"),
    "MBA": ("master", r"(?i:\bmba\b|\bmaster(?:'s)? of business administration\b)"),
    "PhD": ("doctorate", r"(?i:\bph[.\s]*d\b|\bdoctor of philosophy\b)"),
    "Diploma": ("diploma", r"(?i:\bdiploma\b)"),
    "Bachelor's degree": ("bachelor", r"(?i:\bbachelor(?:'?s)?\s+(?:degree|of|in)\b)"),
    "Master's degree": ("master", r"(?i:\bmaster(?:'?s)?\s+(?:degree|of|in)\b)"),
}
EDUCATION = re.compile(r"^(?:education|academic (?:background|qualifications?)|qualifications?)\s*:?", re.I)
WORK = re.compile(r"^(?:(?:professional|work|employment)\s+)?(?:experience|employment|work history)\s*:?", re.I)
OTHER = re.compile(r"^(?:summary|skills|technical skills|projects|certifications?|achievements?|references|interests|contact)\s*:?", re.I)
YEAR = r"(?<!\d)(?:19|20)\d{2}(?!\d)"
NUMBER = r"\d+(?:\.\d+)?"
EXPERIENCE = re.compile(rf"(?P<low>{NUMBER})\s*(?:\+|[-–—]\s*(?P<high>{NUMBER}))?\s*(?P<unit>years?|yrs?|months?|mos?)\b(?:\s+(?P<extra>\d+)\s+months?)?(?:\s+of)?\s+(?:(?:total|professional|work|industry|relevant|commercial|internship)\s+)?experience\b", re.I)
LABELED_EXPERIENCE = re.compile(rf"\b(?:total\s+|work\s+|professional\s+)?experience\s*:\s*(?P<low>{NUMBER})\s*(?:\+|[-–—]\s*(?P<high>{NUMBER}))?\s*(?P<unit>years?|yrs?|months?|mos?)\b(?:\s+(?P<extra>\d+)\s+months?)?", re.I)
FRESHER = re.compile(r"\bfresher\b|\bno (?:prior\s+)?(?:professional|work|industry)\s+experience\b|\bno (?:prior\s+)?experience(?=\s*(?:[.!;]|$|is required|required|needed))|\bexperience\s*:\s*(?:none|nil)\b", re.I)
MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
DATES = re.compile(rf"(?P<start>{MONTH}\s+\d{{4}})\s*(?:-|–|—|to)\s*(?P<end>{MONTH}\s+\d{{4}}|present|current|now)\b", re.I)
MONTHS = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).replace("’", "'")).strip()


def canonical_degree(value):
    value = norm(value)
    compact = re.sub(r"[\W_]", "", value).casefold()
    for name in DEGREES:
        if compact == re.sub(r"[\W_]", "", name).casefold():
            return name
    for name, (_, expr) in DEGREES.items():
        if re.fullmatch(expr, value):
            return name
    return value


def parse_years(value):
    if not str(value).strip():
        return []
    years = set()
    for piece in str(value).split(','):
        match = re.fullmatch(r"\s*((?:19|20)\d{2})(?:\s*[-–]\s*((?:19|20)\d{2}))?\s*", piece)
        if not match:
            raise ValueError("Graduation years: use comma-separated years or ranges, for example 2023, 2024-2026.")
        low, high = int(match[1]), int(match[2] or match[1])
        if high < low:
            raise ValueError("Graduation year ranges must go from the earlier year to the later year.")
        years.update(range(low, high + 1))
    return sorted(years)


def make_requirements(min_years=None, qualifications="", graduation_years="", include_internships=False, relevant_skills="", subjects=""):
    if min_years is not None and (isinstance(min_years, bool) or not isinstance(min_years, (int, float))
                                  or not math.isfinite(min_years) or not 0 <= min_years <= 60):
        raise ValueError("Minimum experience must be between 0 and 60 years; use 0 when freshers are allowed.")
    accepted = [canonical_degree(s) for s in qualifications.split(',') if s.strip()]
    return {"minimum_years": min_years, "accepted_qualifications": list(dict.fromkeys(accepted)),
            "allowed_graduation_years": parse_years(graduation_years), "include_internships": bool(include_internships),
            "relevant_skills": list(dict.fromkeys(s.strip() for s in relevant_skills.split(',') if s.strip())),
            "subjects": list(dict.fromkeys(s.strip() for s in subjects.split(',') if s.strip()))}


SUBJECTS = {
    'computer science': r'computer science(?: and engineering)?|\bCSE\b|\bCS\b',
    'information technology': r'information technology|\bIT\b',
    'mechanical engineering': r'mechanical engineering',
    'electrical engineering': r'electrical engineering',
    'electronics': r'electronics(?: and communication)?(?: engineering)?|\bECE\b',
    'artificial intelligence': r'artificial intelligence',
    'data science': r'data science',
    'mathematics': r'mathematics|maths',
    'statistics': r'statistics',
    'commerce': r'commerce',
}


def subject_present(subject, text):
    key = next((k for k, expr in SUBJECTS.items() if re.fullmatch(expr, subject, re.I)), subject.casefold())
    expr = SUBJECTS.get(key, re.escape(subject))
    matches = list(re.finditer(r'(?<!\w)(?:' + expr + r')(?!\w)', text, re.I))
    return any(not re.search(r'\b(?:not|no|without)\s*$', text[:m.start()], re.I) for m in matches)


def relevant_experience(resume, skill, include_internships=False, today=None):
    """Only explicitly skill-scoped duration claims count; overall tenure cannot prove relevance."""
    term = r'(?<![\w+#])' + re.escape(skill) + r'(?![\w+#])'
    claims = []
    for line, section in _lines(resume):
        if section == 'education' or OTHER.match(line):
            continue
        # Restrict each claim to its own sentence/semicolon clause.
        for clause in re.split(r';|(?<=[.!?])\s+', line):
            patterns = [
                rf'(?P<prefix>(?:no |less than |not |at least )?)(?P<n>{NUMBER})\s*(?P<unit>years?|months?)\s+(?:of\s+)?{term}\s+(?:work\s+)?experience',
                rf'{term}\s+(?:work\s+)?experience\s*:\s*(?P<prefix>(?:no |less than |not |at least )?)(?P<n>{NUMBER})\s*(?P<unit>years?|months?)',
                rf'(?P<prefix>(?:no |less than |not |at least )?)(?P<n>{NUMBER})\s*(?P<unit>years?|months?)\s+(?:of\s+)?experience\s+(?:in|with|using)\s+{term}',
            ]
            for expr in patterns:
                match = re.search(expr, clause, re.I)
                if match and not re.search(r'[\d.+-]$', clause[:match.start()]):
                    claims.append((match, clause))
                    break
    if not claims:
        return {'status': 'review', 'years': None, 'evidence': 'No explicit skill-specific duration found.'}
    values = {float(m['n']) / (12 if m['unit'].lower().startswith('month') else 1) for m, _ in claims}
    uncertain = len(values) != 1 or any(
        m['prefix'].strip().lower() in ('no', 'less than', 'not') or
        re.search(r'\b(?:learning|course|project|academic|not|no|without)\b', clause, re.I) or
        (not include_internships and re.search(r'\bintern(?:ship)?\b', clause, re.I))
        for m, clause in claims)
    years = min(values)
    return {'status': 'review' if uncertain or years > 60 else 'stated', 'years': years,
            'lower_bound_only': any(m['prefix'].strip().lower() == 'at least' for m, _ in claims),
            'evidence': ' | '.join(c for _, c in claims)[:1000]}


def _lines(text):
    section, result = "other", []
    for raw in text.splitlines():
        line = norm(raw).lstrip('#•*- ')
        if EDUCATION.match(line):
            section = "education"
        elif WORK.match(line):
            section = "work"
        elif OTHER.match(line):
            section = "other"
        result.append((line, section))
    return result


def _degree_matches(text, extra=()):
    found = [(name, level) for name, (level, expr) in DEGREES.items() if re.search(expr, text)]
    specific_levels = {level for name, level in found if name not in ("Bachelor's degree", "Master's degree")}
    found = [(name, level) for name, level in found if not (name in ("Bachelor's degree", "Master's degree") and level in specific_levels)]
    for name in extra:
        if name not in DEGREES and re.search(r"(?<!\w)" + re.escape(norm(name)) + r"(?!\w)", text, re.I):
            found.append((name, "custom"))
    return found


def education_evidence(text, accepted=(), today=None):
    today = today or date.today()
    lines = _lines(text)
    has_section = any(section == "education" for _, section in lines)
    entries = []
    for i, (line, section) in enumerate(lines):
        if has_section and section != "education":
            continue
        degrees = _degree_matches(line, accepted)
        if not degrees:
            continue
        block = [line]
        for other, other_section in lines[i + 1:i + 4]:
            if other_section != section or _degree_matches(other, accepted) or OTHER.match(other) or WORK.match(other):
                break
            if other:
                block.append(other)
        evidence = " | ".join(block)
        year_text = ' | '.join(s for s in block if not re.search(r'\b(?:dob|birth|born)\b', s, re.I))
        years = [int(y) for y in re.findall(YEAR, year_text)]
        year = max(years) if years else None
        state = "stated"
        if re.search(r"\b(?:pursuing|expected|ongoing|in progress|currently studying|not completed|incomplete|dropout|dropped out|did not complete|didn't complete|not graduated)\b", evidence, re.I):
            state = "review"
        if re.search(r"\b(?:no|without|do not have|don't have)\s+(?:a\s+)?(?:degree|bachelor|master|b[.\s]*tech|ph[.\s]*d)", evidence, re.I):
            state = "review"
        for name, _ in degrees:
            expr = DEGREES[name][1] if name in DEGREES else re.escape(name)
            match = re.search(expr, line)
            if match and re.search(r"\b(?:no|without|do not have|don't have)\s+(?:a\s+)?$", line[:match.start()], re.I):
                state = "review"
        if any(int(m[2]) < int(m[1]) for m in re.finditer(rf"({YEAR})\s*[-–]\s*({YEAR})", year_text)):
            state = "review"
        if year is not None and year > today.year:
            state = "review"
        for name, level in degrees:
            entries.append({"qualification": name, "level": level, "graduation_year": year,
                            "status": state, "evidence": evidence[:500]})
    return entries


def experience_evidence(text, include_internships=False, today=None):
    today = today or date.today()
    claims, ranges, notes = [], [], []
    lines = _lines(text)
    dated_lines = []
    zero_claim = False
    internship_role = False
    uncertain_dates = False
    uncertain_claim = False
    for i, (line, section) in enumerate(lines):
        if section == "education":
            continue
        is_internship = bool(re.search(r"\bintern(?:ship)?\b", line, re.I))
        if WORK.match(line):
            internship_role = is_internship
        elif section == "work" and (is_internship or re.search(r'\b(?:engineer|developer|analyst|manager|consultant|director|associate|specialist|researcher|assistant)\b', line, re.I)):
            internship_role = is_internship
        ignore = (is_internship or (section == "work" and internship_role)) and not include_internships
        if FRESHER.search(line) and not is_internship and not re.search(r"\bnot (?:a )?fresher\b", line, re.I):
            zero_claim = True
            claims.append({"low": 0.0, "high": 0.0, "evidence": line[:500]})
        for expr in (EXPERIENCE, LABELED_EXPERIENCE):
            for match in expr.finditer(line):
                # A scoped claim is not an overall employment total.
                if expr is LABELED_EXPERIENCE and line[:match.start()].strip() and not re.fullmatch(r'(?:total|overall|professional|work)\s*', line[:match.start()].strip(), re.I):
                    continue
                if re.match(r'\s+(?:in|with|using)\b', line[match.end():], re.I):
                    continue
                if ignore:
                    continue
                factor = 12 if match['unit'].lower().startswith(('month', 'mo')) else 1
                low = float(match['low']) / factor + float(match['extra'] or 0) / 12
                prefix = line[max(0, match.start() - 50):match.start()]
                if re.search(r"\b(?:do not have|don't have|less than|under)\s*$", prefix, re.I):
                    uncertain_claim = True
                lower_bound = '+' in match[0] or re.search(r"\b(?:over|more than|at least)\s*$", prefix, re.I)
                high = float(match['high']) / factor if match['high'] else (None if lower_bound else low)
                if low > 60 or (high is not None and (high < low or high > 60)):
                    notes.append("An experience duration is invalid or ambiguous.")
                    continue
                claims.append({"low": low, "high": high, "evidence": line[:500]})
        if section != "work":
            continue
        if ignore:
            notes.append("Internship dates were excluded from the work-experience total.")
            continue
        for match in DATES.finditer(line):
            def month_index(value):
                if value.lower() in ('present', 'current', 'now'):
                    return today.year * 12 + today.month - 1
                month, year = value.split()
                return int(year) * 12 + MONTHS[month[:3].lower()] - 1
            start, end = month_index(match['start']), month_index(match['end'])
            if start > end or end > today.year * 12 + today.month - 1:
                uncertain_dates = True
                continue
            ranges.append((start, end))
            dated_lines.append(line[:500])
        if re.search(rf"{YEAR}\s*[-–—]\s*(?:{YEAR}|present)", line, re.I) and not DATES.search(line):
            uncertain_dates = True
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    years_from_dates = sum(end - start for start, end in merged) / 12 if merged else None
    if claims:
        # Different scoped totals are not added or silently resolved by taking the largest.
        unique = {(c['low'], c['high']) for c in claims}
        conflict = uncertain_claim or len(unique) > 1 or (zero_claim and years_from_dates is not None and years_from_dates > 0)
        low, high = next(iter(unique))
        return {"status": "review" if conflict else "stated", "minimum_years": low,
                "maximum_years": high, "method": "Explicit resume statement",
                "evidence": list(dict.fromkeys(c['evidence'] for c in claims)),
                "notes": list(dict.fromkeys(notes + (["Multiple experience statements conflict or describe different scopes; review them."] if conflict else [])))}
    if years_from_dates is not None:
        return {"status": "review" if uncertain_dates else "stated", "minimum_years": years_from_dates,
                "maximum_years": years_from_dates, "method": "Month/year employment dates; overlaps counted once",
                "evidence": dated_lines, "notes": list(dict.fromkeys(notes + ["Month-level estimate; relevance, employment type and partial months need review."] + (["Some work dates lack months or are invalid."] if uncertain_dates else [])))}
    return {"status": "review" if uncertain_dates else "missing", "minimum_years": None, "maximum_years": None,
            "method": "No usable total", "evidence": [],
            "notes": list(dict.fromkeys(notes + ["Add an explicit total such as 'Work experience: 2 years', or month/year employment dates. Freshers can state 'Work experience: 0 years'."]))}


def suggest_requirements(job):
    years = []
    for expr in (EXPERIENCE, LABELED_EXPERIENCE):
        for match in expr.finditer(norm(job)):
            years.append(float(match['low']) / (12 if match['unit'].lower().startswith(('month', 'mo')) else 1) + float(match['extra'] or 0) / 12)
    if not years and FRESHER.search(job):
        years = [0.0]
    qualifications = list(dict.fromkeys(name for name, _ in _degree_matches(norm(job))))
    batches = []
    for line in job.splitlines():
        if re.search(r"graduat|pass(?:ed)?[ -]?out|year of passing|batch", line, re.I):
            for match in re.finditer(rf"({YEAR})(?:\s*[-–]\s*({YEAR}))?", line):
                low, high = int(match[1]), int(match[2] or match[1])
                if low <= high:
                    batches.extend(range(low, high + 1))
    years = [y for y in years if 0 <= y <= 60]
    return {"minimum_years": min(years) if years else None,
            "qualifications": ', '.join(qualifications), "graduation_years": ', '.join(map(str, sorted(set(batches))))}


def check_requirements(resume, requirements=None, today=None):
    cfg = requirements or make_requirements()
    today = today or date.today()
    experience = experience_evidence(resume, cfg['include_internships'], today)
    education = education_evidence(resume, cfg['accepted_qualifications'], today)
    rows = []
    def row(name, status, expected, observed, evidence, action):
        rows.append({"requirement": name, "status": status, "expected": expected, "observed": observed,
                     "evidence": evidence, "action": action})
    minimum = cfg['minimum_years']
    exp_status = experience['status']
    expected = f"At least {minimum:g} years" if minimum is not None else "Set the JD minimum (0 if freshers are allowed)"
    observed = "Not found" if experience['minimum_years'] is None else f"{experience['minimum_years']:.2f} years" + (" or more" if experience['maximum_years'] is None else f" to {experience['maximum_years']:.2f} years" if experience['maximum_years'] != experience['minimum_years'] else "")
    status = "missing" if exp_status == "missing" else "review" if exp_status == "review" or minimum is None else "met" if experience['minimum_years'] >= minimum else "not_met" if experience['maximum_years'] is not None and experience['maximum_years'] < minimum else "review"
    row("Work experience", status, expected, observed, ' | '.join(experience['evidence']),
        "Confirm the JD minimum and add truthful total work experience or employment dates. A missing statement is not treated as zero.")
    accepted = cfg['accepted_qualifications']
    def matches(entry):
        return any(entry['qualification'] == q or (q == "Bachelor's degree" and entry['level'] == 'bachelor')
                   or (q == "Master's degree" and entry['level'] == 'master') for q in accepted)
    matching = [e for e in education if matches(e)]
    subjects = cfg.get('subjects', [])
    subject_matching = [e for e in matching if any(subject_present(s, e['evidence']) for s in subjects)] if subjects else matching
    completed = [e for e in matching if e['status'] == 'stated']
    qualification_status = "missing" if not education else "review" if not accepted else "met" if completed else "review" if matching else "not_met"
    row("Qualification", qualification_status, 'Any one of: ' + ', '.join(accepted) if accepted else "Set the accepted qualification(s) from the JD",
        ', '.join(dict.fromkeys(e['qualification'] for e in education)) or "Not found",
        ' | '.join(e['evidence'] for e in (matching or education)),
        "State the completed qualification clearly. List each JD-accepted alternative; equivalence and subject requirements must be checked against the evidence.")
    candidates = subject_matching if subjects else matching or education
    dated = [e for e in candidates if e['graduation_year'] is not None]
    allowed = cfg['allowed_graduation_years']
    valid = [e for e in dated if e['status'] == 'stated' and (not allowed or e['graduation_year'] in allowed)]
    grad_status = "met" if valid else "missing" if not dated else "review" if any(e['status'] == 'review' for e in dated) else "not_met"
    row("Graduation / pass-out year", grad_status, ', '.join(map(str, allowed)) if allowed else "A graduation year must be stated; no JD batch restriction configured",
        ', '.join(map(str, sorted({e['graduation_year'] for e in dated}))) or "Not found beside a qualification",
        ' | '.join(e['evidence'] for e in dated),
        "Add the pass-out year beside the relevant qualification. Expected completion is flagged for review; birth and employment years are not graduation evidence.")
    if subjects:
        subject_status = 'met' if any(e['status'] == 'stated' for e in subject_matching) else 'review'
        if matching and not subject_matching and all(any(subject_present(s, e['evidence']) for s in SUBJECTS) for e in matching):
            subject_status = 'not_met'
        row('Degree subject', subject_status, 'Any one of: ' + ', '.join(subjects),
            'Subject found beside an accepted qualification' if subject_matching else 'No accepted subject confirmed beside an accepted qualification',
            ' | '.join(e['evidence'] for e in matching),
            'Check the specialization beside the accepted degree. Related disciplines and equivalence need manual review.')
    for skill in cfg.get('relevant_skills', []):
        relevant = relevant_experience(resume, skill, cfg['include_internships'], today)
        state = 'review' if relevant['status'] != 'stated' or minimum is None else 'met' if relevant['years'] >= minimum else 'review' if relevant.get('lower_bound_only') else 'not_met'
        row('Relevant experience: ' + skill, state, expected + ' using ' + skill,
            'Not confirmed' if relevant['years'] is None else f"{relevant['years']:g} years stated",
            relevant['evidence'], 'State a truthful skill-specific duration, for example Python experience: 2 years. Overall employment duration alone does not confirm relevant experience.')
    summary = "Does not meet configured checks" if any(r['status'] == 'not_met' for r in rows) else "Needs review" if any(r['status'] != 'met' for r in rows) else "Meets configured checks"
    return {"summary": summary, "settings": cfg, "checks": rows, "experience": experience, "education": education,
            "note": "Mandatory detail checks use resume statements and explicit JD settings. Missing or unclear details cannot pass. These checks do not verify credentials, relevant experience, degree equivalence or final job eligibility."}
