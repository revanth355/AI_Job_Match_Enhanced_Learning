"""In-memory, paginated PDF reports with escaped user text and bundled Unicode font."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether, PageBreak
from .summary import report_summary


def pdf_report(result):
    # Vera is distributed with ReportLab; no system font or network required.
    import reportlab
    font_dir = Path(reportlab.__file__).parent / "fonts"
    if "SkillBridge" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SkillBridge", str(font_dir / "Vera.ttf")))
        pdfmetrics.registerFont(TTFont("SkillBridgeBold", str(font_dir / "VeraBd.ttf")))
        pdfmetrics.registerFontFamily("SkillBridge", normal="SkillBridge", bold="SkillBridgeBold", italic="SkillBridge", boldItalic="SkillBridgeBold")
    styles = getSampleStyleSheet()
    for key in ("Normal", "BodyText", "Title", "Heading1", "Heading2", "Heading3"):
        styles[key].fontName = "SkillBridgeBold" if key != "BodyText" and key != "Normal" else "SkillBridge"
        styles[key].textColor = colors.HexColor("#172b46")
        styles[key].wordWrap = None
        styles[key].splitLongWords = 1
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 14
    styles["BodyText"].spaceAfter = 7
    styles.add(ParagraphStyle("SmallNote", parent=styles["BodyText"], fontSize=8, leading=12, spaceAfter=3))
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=44, leftMargin=44,
                            topMargin=45, bottomMargin=44, title="SkillBridge Job Match Report",
                            author="SkillBridge")
    story = []

    def safe(text):
        # Font coverage is Latin/Greek/Cyrillic. Escape markup and visibly replace
        # unsupported glyphs instead of silently rendering missing-glyph boxes.
        font = pdfmetrics.getFont("SkillBridge")
        cleaned = "".join(c if c in "\n\t" or ord(c) in font.face.charToGlyph else "?" for c in str(text) if c in "\n\t" or ord(c) >= 32)
        return escape(cleaned).replace("\n", "<br/>")

    def para(text, style="BodyText"):
        story.append(Paragraph(safe(text), styles[style]))

    def heading(text):
        para(text, "Heading2")

    def link(resource):
        label = resource["title"] + " (" + ("curated" if resource["curated"] else "unreviewed search") + ")"
        story.append(Paragraph(f'<link href={quoteattr(resource["url"])} color="#146b77">{safe(label)}</link>', styles["SmallNote"]))
        para(resource["url"], "SmallNote")

    para("SkillBridge", "Title")
    para("Resume and job match report", "Heading2")
    para("Text similarity measures document similarity. It is not a hiring probability or ATS score.")
    para("This report contains document excerpts; review before sharing. Unsupported PDF font characters appear as '?'. JSON and Markdown preserve original text.", "SmallNote")
    para("Engine: " + result["model"])
    para(f"Text similarity: {result['text_similarity']} / 100")
    value = result["skill_coverage"]
    para("Detected skill coverage: " + (f"{value}%" if value is not None else "N/A"))
    summary = report_summary(result)
    heading('At a glance')
    para(summary['status'], 'Heading3')
    para('Mandatory checks: ' + summary['mandatory_status'])
    para(f"Matched skills: {summary['matched_count']} of {summary['job_skill_count']}")
    # Bound the overview; complete skill lists and evidence follow on later pages.
    def brief(items):
        return ', '.join(items[:8]) + (f' (+{len(items) - 8} more; see details)' if len(items) > 8 else '') if items else 'None'
    para('Matched: ' + brief(result['matched_skills']))
    para('Missing required skill evidence: ' + brief(summary['required_gaps']))
    para('Missing JD settings: ' + brief(summary['missing_jd_settings']))
    para('Missing resume details: ' + brief(summary['missing_resume_details']))
    heading('Your next three actions')
    for index, action in enumerate(summary['top_actions'], 1):
        para(f'{index}. {action}')
    para(summary['score_explanation'], 'SmallNote')
    para(summary['note'], 'SmallNote')
    para(summary['input_note'], 'SmallNote')
    story.append(PageBreak())
    review = result.get("requirement_review")
    if review:
        heading("Mandatory resume details")
        para(review['summary'])
        para(review['note'], "SmallNote")
        for check in review['checks']:
            start = len(story)
            para(check['requirement'] + ': ' + check['status'].replace('_', ' '), "Heading3")
            para('JD setting: ' + check['expected'])
            para('Resume: ' + check['observed'])
            para('Evidence: ' + (check['evidence'] or 'Not found'))
            if check['status'] != 'met':
                para(check['action'], "SmallNote")
            section = story[start:]
            story[start:] = [KeepTogether(section)]
        para('Experience method: ' + review['experience']['method'], "SmallNote")
        for note in review['experience']['notes']:
            para(note, "SmallNote")
    heading("Requirement priorities")
    for priority, skills in result["job_skills_by_priority"].items():
        start = len(story)
        value = result[priority + "_coverage"]
        para(f"{priority.title()} - coverage: " + (f"{value}%" if value is not None else "N/A"), "Heading3")
        para("Detected: " + (", ".join(skills) or "None"))
        para("To review: " + (", ".join(result["missing_by_priority"][priority]) or "None"))
        section = story[start:]
        story[start:] = [KeepTogether(section)]
    heading("Skills overview")
    for label, key in [("Positive evidence in both", "matched_skills"), ("Without positive resume evidence", "skills_not_found"), ("Other resume skills", "additional_skills")]:
        para(label + ": " + (", ".join(result[key]) or "None"))
    heading("Suggested next steps")
    for item in result["suggestions"]:
        para(item)
    heading("Practice plan")
    for item in result["learning_plan"]:
        start = len(story)
        para(f"{item['skill']} - {item['priority']} / resume: {item['resume_status']}", "Heading3")
        for key in ("goal", "practice", "check", "proof"):
            para(key.title() + ": " + item[key])
        if item["resource_url"]:
            para(item["resource_title"] + ": " + item["resource_url"], "SmallNote")
        else:
            para(item["resource_note"], "SmallNote")
        section = story[start:]
        story[start:] = [KeepTogether(section)]
    heading("Skill evidence")
    for row in result["evidence"]:
        para(f"{row['skill']} - {row['priority']} / resume: {row['resume_status']}", "Heading3")
        para("Resume: " + row["resume_evidence"])
        para("Job: " + row["job_evidence"])
    heading("Resume mentions needing context review")
    if all(entry["status"] == "mentioned" for entry in result["resume_context"].values()):
        para("No learning, negative or conflicting mentions detected.")
    for skill, entry in result["resume_context"].items():
        if entry["status"] == "mentioned":
            continue
        para(f"{skill}: {entry['status']}", "Heading3")
        for mention in entry["mentions"]:
            para(mention["status"] + ": " + mention["evidence"])
    heading("Job skills explicitly not required")
    for skill, entry in result["excluded_job_skills"].items():
        para(skill + ": " + entry["evidence"])
    if not result["excluded_job_skills"]:
        para("None detected.")
    daily = result.get("daily_plan")
    if daily:
        heading("Daily study plan")
        para(f"Requested: {daily['requested_days']} days. Scheduled: {daily['total_days']} days. Budget: up to {daily['minutes_per_day']} minutes/day.")
        para(f"Completed days: {len(daily['completed_days'])}. Each session: 10 minutes learn, 15 minutes practice, 5 minutes review.")
        para("Daily self-check: save your result and explain the steps without copying. Repeat or extend the exercise if needed.")
        para(daily["note"], "SmallNote")
        if daily["extended"]:
            para("The schedule was extended to include every starter topic within your daily budget.")
        if not daily["days"]:
            para("No study tasks: no detected skill gaps need a plan.")
        for day in daily["days"]:
            start = len(story)
            status = "complete" if day["day"] in daily["completed_days"] else "to do"
            para(f"Day {day['day']} - {day['minutes']} minutes / {status}", "Heading3")
            for session in day["sessions"]:
                para(f"{session['skill']} / {session['topic']} ({session['priority']}; {session['curriculum']})")
                para("Practice: " + session["practice"])
                if 'lesson' in session:
                    para('Level: ' + session['level'] + ' | Prerequisite: ' + session['prerequisite'], 'SmallNote')
                    para('Lesson: ' + session['lesson'], 'SmallNote')
                    para('Challenge: ' + session['challenge'], 'SmallNote')
                    para('Self-check: ' + session['topic_question'], 'SmallNote')
                    if session.get('quiz'):
                        quiz_start = len(story)
                        quiz = session['quiz']
                        para('Quiz: ' + quiz['question'], 'SmallNote')
                        para(' | '.join(f'{i+1}. {option}' for i, option in enumerate(quiz['options'])), 'SmallNote')
                        para('Answer: ' + quiz['options'][quiz['answer']] + '. ' + quiz['explanation'], 'SmallNote')
                        quiz_block = story[quiz_start:]
                        story[quiz_start:] = [KeepTogether(quiz_block)]
            section = story[start:]
            # Personalized sessions may exceed a page at 120 minutes/day.
            # Allow natural page breaks instead of forcing a whole day together.
            story[start:] = section
        heading("Video and reading links for your daily plan")
        seen = set()
        for day in daily["days"]:
            for session in day["sessions"]:
                if session["skill"] in seen:
                    continue
                seen.add(session["skill"])
                start = len(story)
                para(session["skill"], "Heading3")
                # Prefer a curated video; a clearly marked search is the fallback.
                video = next((r for r in session["resources"] if r["kind"] == "video"),
                             next(r for r in session["resources"] if r["kind"] == "video search"))
                reading = next(r for r in session["resources"] if r["kind"] in ("reading", "reading search"))
                link(video)
                link(reading)
                section = story[start:]
                story[start:] = [KeepTogether(section)]
    heading("Limitations and privacy")
    for item in result["limitations"]:
        para(item)

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("SkillBridge", 8)
        canvas.setFillColor(colors.HexColor("#52657c"))
        canvas.drawString(44, 25, "SkillBridge | Candidate self-review")
        canvas.drawRightString(A4[0] - 44, 25, f"Page {document.page}")
        canvas.restoreState()

    # Keep a section heading with its first block, including a practice card.
    grouped, pending = [], []
    for flowable in story:
        if isinstance(flowable, Paragraph) and flowable.style.name.startswith("Heading"):
            pending.append(flowable)
        elif pending:
            grouped.append(KeepTogether(pending + [flowable]))
            pending = []
        else:
            grouped.append(flowable)
    grouped.extend(pending)
    doc.build(grouped, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()
