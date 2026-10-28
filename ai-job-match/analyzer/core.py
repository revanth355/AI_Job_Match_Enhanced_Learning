"""Evidence-based skill extraction and explicitly labeled similarity modes."""
import json
import re
import unicodedata
from pathlib import Path
from functools import lru_cache
from .context import detect_context
from .plans import learning_step, build_daily_plan
from .requirements import check_requirements
from .summary import report_summary

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CHARS = 60000


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


@lru_cache(maxsize=1)
def taxonomy():
    return json.loads((Path(__file__).resolve().parents[1] / "data/skills.json").read_text())


def pattern(alias):
    # Punctuation-aware boundaries prevent Java/JavaScript and C/C++ confusion.
    return re.compile(r"(?<![\w+#])" + re.escape(normalize(alias)).replace(r"\ ", r"\s+") + r"(?![\w+#])")


def skill_context(text, custom=(), job=False):
    catalog = {k: list(dict.fromkeys([k, *v])) for k, v in taxonomy().items()}
    existing = {normalize(a) for aliases in catalog.values() for a in aliases}
    for skill in custom:
        skill = skill.strip()
        if skill and normalize(skill) not in existing:
            catalog[skill] = [skill]
            existing.add(normalize(skill))
    return detect_context(text, catalog, normalize, pattern, job)


def find_skills(text, custom=()):
    return {s: v["evidence"] for s, v in skill_context(text, custom).items()
            if v["status"] == "mentioned"}


@lru_cache(maxsize=1)
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def semantic_similarity(resume, job, model=None):
    model = model if model is not None else load_model()
    # Tokenizer-aware splitting guarantees all document tokens are considered.
    def embed_document(text):
        ids = model.tokenizer.encode(text, add_special_tokens=False)
        size = max(1, int(model.max_seq_length) - 2)
        pieces = [model.tokenizer.decode(ids[i:i + size], skip_special_tokens=True)
                  for i in range(0, len(ids), size)]
        if not pieces:
            raise ValueError("The model could not tokenize the text.")
        vectors = model.encode(pieces, normalize_embeddings=True, show_progress_bar=False)
        weights = [len(ids[i:i + size]) for i in range(0, len(ids), size)]
        return np.average(vectors, axis=0, weights=weights).reshape(1, -1)
    raw = float(cosine_similarity(embed_document(resume), embed_document(job))[0, 0])
    return round(max(0.0, min(1.0, raw)) * 100, 1)


def keyword_similarity(resume, job):
    try:
        vectors = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                  token_pattern=r"(?u)\b\w[\w+#.]*\b").fit_transform([resume, job])
    except ValueError:
        return 0.0
    return round(float(cosine_similarity(vectors[0], vectors[1])[0, 0]) * 100, 1)


def analyze(resume, job, mode="keyword", custom=(), model=None, requirements=None):
    for label, text in [("Resume", resume), ("Job description", job)]:
        if len(text.strip()) < 40 or len(text.split()) < 5:
            raise ValueError(f"{label}: enter at least 40 characters and 5 words.")
        if len(text) > MAX_CHARS:
            raise ValueError(f"{label}: maximum {MAX_CHARS:,} characters.")
    if mode not in {"keyword", "semantic"}:
        raise ValueError("Choose keyword or semantic mode.")
    rcontext, jcontext = skill_context(resume, custom), skill_context(job, custom, job=True)
    rskills = {s: v["evidence"] for s, v in rcontext.items() if v["status"] == "mentioned"}
    jskills = {s: v["evidence"] for s, v in jcontext.items() if v["status"] != "excluded"}
    matched = sorted(set(rskills) & set(jskills))
    missing = sorted(set(jskills) - set(rskills))
    additional = sorted(set(rskills) - set(jskills))
    groups = {priority: sorted(s for s in jskills if jcontext[s]["status"] == priority)
              for priority in ("required", "preferred", "unspecified")}
    def coverage(skills):
        return round(100 * len(set(skills) & set(matched)) / len(skills), 1) if skills else None
    missing_by_priority = {p: sorted(set(skills) - set(matched)) for p, skills in groups.items()}
    evidence = [{"skill": s, "priority": jcontext[s]["status"],
                 "resume_status": rcontext.get(s, {}).get("status", "not found"),
                 "resume_evidence": rcontext.get(s, {}).get("evidence", "Not found"),
                 "job_evidence": jskills[s]} for s in sorted(jskills)]
    suggestions = [
        "For each matched skill, add a specific project example and a measurable result, if you have one.",
        "Keep headings clear: Summary, Skills, Projects, Experience and Education.",
    ]
    if missing:
        suggestions.insert(0, "Review skills without positive resume evidence. Prioritize required skills, then unspecified and preferred skills. Add claims only if you can demonstrate them.")
    if missing_by_priority["required"]:
        suggestions.insert(0, "Required skills to review first: " + ", ".join(missing_by_priority["required"]) + ".")
    if not jskills:
        suggestions.insert(0, "No catalog skills were detected in the job description. Add relevant custom skills and analyze again.")
    similarity = (semantic_similarity(resume, job, model) if mode == "semantic"
                  else keyword_similarity(resume, job))
    learning_plan = [learning_step(s, p, rcontext.get(s, {}).get("status", "not found"))
                     for p in ("required", "unspecified", "preferred") for s in missing_by_priority[p]]
    result = {
        "mode": mode,
        "model": MODEL_NAME if mode == "semantic" else "TF-IDF (unigrams + bigrams)",
        "text_similarity": similarity,
        "skill_coverage": round(100 * len(matched) / len(jskills), 1) if jskills else None,
        "required_coverage": coverage(groups["required"]),
        "preferred_coverage": coverage(groups["preferred"]),
        "unspecified_coverage": coverage(groups["unspecified"]),
        "job_skills_by_priority": groups,
        "missing_by_priority": missing_by_priority,
        "resume_context": rcontext,
        "excluded_job_skills": {s: v for s, v in jcontext.items() if v["status"] == "excluded"},
        "matched_skills": matched, "skills_not_found": missing, "additional_skills": additional,
        "evidence": evidence,
        "suggestions": suggestions,
        "learning_plan": learning_plan,
        "daily_plan": build_daily_plan(learning_plan),
        "requirement_review": check_requirements(resume, requirements),
        "limitations": [
            "Similarity is not a hiring probability, an ATS score or a measure of candidate quality.",
            "Skills are dictionary-based mentions, not verified proficiency. English context rules can miss negation, complex lists and unusual phrasing; review evidence.",
            "Learning, negated and conflicting mentions do not count as positive skill evidence. Positive mentions do not prove proficiency.",
            "Required/preferred labels are inferred from explicit cues and headings. Unmarked skills remain unspecified. All-skill coverage is unweighted; category coverage is separate.",
            "Experience, qualification and graduation checks compare resume statements with configured requirements; they do not verify credentials or final eligibility. Curated practice tasks are templates.",
            "No readable evidence does not mean the candidate lacks the skill. English text works best.",
            "Names, contact details and unrelated content can influence whole-document text similarity.",
        ],
    }
    result['summary'] = report_summary(result)
    return result


def markdown_report(result):
    coverage = result["skill_coverage"]
    summary = report_summary(result)
    lines = ["# Job Match Report", "", f"Mode: {result['mode']}",
             f"Model: {result['model']}", f"Text similarity: {result['text_similarity']} / 100",
             f"Skill coverage: {str(coverage) + '%' if coverage is not None else 'N/A'}", "",
             "## At a glance", summary['status'],
             'Mandatory checks: ' + summary['mandatory_status'],
             f"Matched skills: {summary['matched_count']} of {summary['job_skill_count']}",
             'Matched: ' + (', '.join(result['matched_skills']) or 'None detected'),
             'Missing required skill evidence: ' + (', '.join(summary['required_gaps']) or 'None detected'),
             'Missing JD settings: ' + (', '.join(summary['missing_jd_settings']) or 'None'),
             'Missing resume details: ' + (', '.join(summary['missing_resume_details']) or 'None'),
             '', '### Your next three actions',
             *[f'{i}. {action}' for i, action in enumerate(summary['top_actions'], 1)],
             '', summary['score_explanation'], summary['note'], summary['input_note'], '',
             "## Mandatory resume details"]
    review = result.get("requirement_review")
    if review:
        lines += [review["summary"], review["note"], ""]
        for check in review["checks"]:
            lines += [f"### {check['requirement']}: {check['status']}", "JD setting: " + check['expected'],
                      "Resume: " + check['observed'], "Evidence: " + (check['evidence'] or 'Not found'), check['action'], ""]
        lines += ["Experience method: " + review['experience']['method'], *review['experience']['notes'], ""]
    lines += ["## Matching skills", ", ".join(result["matched_skills"]) or "None detected", "",
             "## Job skills not found in resume", ", ".join(result["skills_not_found"]) or "None detected", "",
             "## Requirement priorities"]
    for priority, skills in result["job_skills_by_priority"].items():
        value = result[priority + "_coverage"]
        lines += [f"### {priority.title()}", "Skills: " + (", ".join(skills) or "None detected"),
                  "Coverage: " + (f"{value}%" if value is not None else "N/A"),
                  "To review: " + (", ".join(result["missing_by_priority"][priority]) or "None"), ""]
    lines += ["## Suggestions", *[f"- {x}" for x in result["suggestions"]], "", "## Learning plan"]
    for x in result["learning_plan"]:
        lines += [f"### {x['skill']} ({x['priority']}; resume: {x['resume_status']})", x["goal"],
                  x["practice"], "Check: " + x["check"], x["proof"],
                  f"Resource: {x['resource_title']} - {x['resource_url']}" if x["resource_url"] else x["resource_note"], ""]
    daily = result.get("daily_plan")
    if daily:
        lines += ["## Daily study plan", f"Requested: {daily['requested_days']} days; budget: up to {daily['minutes_per_day']} minutes/day.",
                  f"Scheduled: {daily['total_days']} days. Completed days: {len(daily['completed_days'])}.", daily["note"], ""]
        if daily["extended"]:
            lines += ["The schedule was extended so no detected gap or starter topic is left out.", ""]
        if not daily["days"]:
            lines += ["No study tasks: no job skills without positive resume evidence were detected.", ""]
        for day in daily["days"]:
            state = "complete" if day["day"] in daily["completed_days"] else "to do"
            lines += [f"### Day {day['day']} ({day['minutes']} minutes; {state})"]
            for session in day["sessions"]:
                lines += [f"#### {session['skill']} / {session['topic']} ({session['priority']})", session["curriculum"],
                          session["goal"], "Practice: " + session["practice"], "Check: " + session["check"]]
                if 'lesson' in session:
                    lines += ['Level: ' + session['level'], 'Prerequisites: ' + session['prerequisite'],
                              'Lesson: ' + session['lesson'], 'Challenge: ' + session['challenge'],
                              'Self-check: ' + session['topic_question'], *['- ' + item for item in session['rubric']]]
                    if session.get('quiz'):
                        quiz = session['quiz']
                        lines += ['Quiz: ' + quiz['question'], *[f'{i+1}. {option}' for i, option in enumerate(quiz['options'])],
                                  'Answer: ' + quiz['options'][quiz['answer']] + '. ' + quiz['explanation']]
                lines.extend(f"- {r['kind']}: {r['title']} - {r['url']} ({'curated' if r['curated'] else 'unreviewed search'})" for r in session["resources"])
            lines.append("")
    lines += ["", "## Evidence"]
    for row in result["evidence"]:
        lines += [f"### {row['skill']} ({row['priority']}; resume: {row['resume_status']})", f"Resume: {row['resume_evidence']}", f"Job: {row['job_evidence']}", ""]
    lines += ["## Resume context details"]
    for skill, entry in result["resume_context"].items():
        lines += [f"### {skill}: {entry['status']}", *[f"- {m['status']}: {m['evidence']}" for m in entry["mentions"]]]
    lines += ["", "## Job skills explicitly not required"]
    for skill, entry in result["excluded_job_skills"].items():
        lines += [f"- {skill}: {entry['evidence']}"]
    return "\n".join(lines + ["## Limitations", *[f"- {x}" for x in result["limitations"]]])
