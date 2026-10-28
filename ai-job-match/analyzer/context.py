"""Conservative English rules for skill mentions; never verifies proficiency."""
import re


REQUIRED = r"\b(?:required|requirements|must[- ]have|must|mandatory|essential|minimum qualifications)\b"
PREFERRED = r"\b(?:preferred|preferable|desirable|nice[- ]to[- ]have|optional|bonus|a plus)\b"
NEGATIVE = r"\b(?:no (?:prior )?(?:experience|knowledge|proficiency|skills?|background)(?:\s+(?:in|with|of))?|not (?:experienced|proficient|familiar)(?:\s+(?:in|with))?|lack(?:ing)?(?:\s+(?:experience|knowledge|skills?))?(?:\s+(?:in|with|of))?|do not know|don't know|never used|without (?:experience|knowledge)(?:\s+(?:in|with|of))?)\b"
LEARNING = r"\b(?:learning|studying|beginner(?: in)?|plan(?:ning)? to learn|want to learn|interested in learning|currently learning)\b"
POSITIVE = r"\b(?:experienced in|proficient in|skilled in|built with|used|developed with|worked with)\b"


def clauses(text):
    """Keep C#, C++ and dotted product names intact when splitting prose."""
    for line in text.splitlines():
        yield from (s.strip() for s in re.split(r"(?<=[.!?])\s+|;|\bbut\b|\bhowever\b", line) if s.strip())


def resume_status(clause, start, end, section="mentioned"):
    before, after = clause[:start], clause[end:]
    cues = []
    for status, expr in [("negated", NEGATIVE), ("learning", LEARNING), ("mentioned", POSITIVE)]:
        cues.extend((m.start(), status) for m in re.finditer(expr, before))
    if re.match(r"\s*[:(-]?\s*(?:currently )?(?:learning|beginner|in progress)\b", after):
        return "learning"
    if re.match(r"\s*[:(-]?\s*(?:no experience|not (?:known|proficient)|not familiar)\b", after):
        return "negated"
    if re.search(r"\b(?:no|not|without)\s*$", before):
        return "negated"
    return max(cues)[1] if cues else section


def job_status(clause, start, end, section):
    before, after = clause[:start], clause[end:]
    markers = [(m.start(), kind) for kind, expr in [("required", REQUIRED), ("preferred", PREFERRED)]
               for m in re.finditer(expr, clause)]
    if len(markers) == 1 and re.search(r"\bnot (?:required|necessary|needed)\s*[.!]?\s*$", clause):
        return "excluded"
    if re.match(r"\s*(?:experience\s+)?(?:is\s+|are\s+)?(?:not required|not necessary|not needed)\b", after):
        return "excluded"
    if re.search(r"\b(?:no|without)\b", before) and re.search(r"\b(?:required|necessary|needed)\b", after):
        return "excluded"
    if re.search(r"\b(?:not required|not necessary|not needed)\s*:?\s*$", before):
        return "excluded"
    # A nearby following cue handles 'Python required, Docker preferred'.
    following = re.split(r",|\band\b", after, maxsplit=1)[0]
    if re.search(PREFERRED, following):
        return "preferred"
    if re.search(REQUIRED, following):
        return "required"
    cues = [(m.start(), kind) for kind, expr in [("required", REQUIRED), ("preferred", PREFERRED)]
            for m in re.finditer(expr, before)]
    return max(cues)[1] if cues else markers[0][1] if len(markers) == 1 else section


def detect_context(text, catalog, normalize, pattern, job=False):
    found = {}
    section = "unspecified"
    resume_section = "mentioned"
    for raw in clauses(text):
        clause = normalize(raw)
        all_spans = {name: set((m.start(), m.end()) for alias in aliases
                              for m in pattern(alias).finditer(clause))
                     for name, aliases in catalog.items()}
        cue_chars = list(clause)
        for spans in all_spans.values():
            for start, end in spans:
                cue_chars[start:end] = " " * (end - start)
        cue_clause = "".join(cue_chars)
        if not job:
            if re.match(r"^[\s#*\-\u2022]*(?:currently learning|learning|studying|skills in progress)\s*(?::|$)", clause):
                resume_section = "learning"
            elif re.match(r"^[\s#*\-\u2022]*(?:no experience|not familiar)\s*(?::|$)", clause):
                resume_section = "negated"
            elif re.match(r"^[\s#*\-\u2022]*(?:skills|technical skills|projects|experience|work experience|education|summary|certifications)\s*(?::|$)", clause):
                resume_section = "mentioned"
        # Only explicit leading headings carry over to subsequent lines.
        heading = re.match(r"^[\s#*\-\u2022]*(required(?: skills| qualifications)?|requirements|must[- ]have(?: skills)?|minimum qualifications|preferred(?: skills| qualifications)?|nice[- ]to[- ]have(?: skills)?|optional(?: skills)?|bonus)\s*(?::|$)", clause)
        if heading:
            section = "preferred" if re.search(PREFERRED, heading.group(1)) else "required"
        elif re.match(r"^[\s#*\-\u2022]*(?:responsibilities|about us|benefits|education|experience|other|duties)\s*(?::|$)", clause):
            section = "unspecified"
        for name, spans in all_spans.items():
            for start, end in sorted(spans):
                status = job_status(clause, start, end, section) if job else resume_status(cue_clause, start, end, resume_section)
                item = {"status": status, "evidence": re.sub(r"\s+", " ", raw)[:500]}
                mentions = found.setdefault(name, [])
                if item not in mentions:
                    mentions.append(item)
    result = {}
    for name, mentions in found.items():
        states = {m["status"] for m in mentions}
        if job:
            status = next(s for s in ("required", "unspecified", "preferred", "excluded") if s in states)
        else:
            status = "review" if "mentioned" in states and "negated" in states else next(
                s for s in ("mentioned", "learning", "negated") if s in states)
        evidence = next((m["evidence"] for m in mentions if m["status"] == status), mentions[0]["evidence"])
        result[name] = {"status": status, "evidence": evidence, "mentions": mentions}
    return result
