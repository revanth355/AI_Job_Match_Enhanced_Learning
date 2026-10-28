"""Run with: python -m streamlit run app.py"""
from pathlib import Path
import json
import hashlib
import streamlit as st
from analyzer.core import analyze, markdown_report, skill_context
from analyzer.extraction import extract_text
from analyzer.reports import pdf_report
from analyzer.plans import build_daily_plan
from analyzer.requirements import make_requirements, suggest_requirements, experience_evidence, education_evidence
from analyzer.summary import report_summary
from analyzer.lessons import LEVELS
from analyzer.progress import plan_key, export_progress, import_progress

ROOT = Path(__file__).parent
st.set_page_config(page_title="SkillBridge • Job Match", page_icon="🔎", layout="wide")
st.markdown("""<style>
.block-container {max-width:1200px;padding-top:2.5rem;}
[data-testid="stMetric"] {background:#13213a;border:1px solid #293b59;
 padding:20px;border-radius:16px;}
.eyebrow {color:#56dcc4;font-size:.8rem;letter-spacing:.18em;font-weight:700;}
.hero {font-size:3rem;font-weight:800;line-height:1.12;margin:.6rem 0 1rem;}
.intro {color:#aebfd6;font-size:1.08rem;max-width:760px;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🔎 SkillBridge")
    st.caption("YOUR NEXT ROLE, WITH CLARITY")
    st.divider()
    engine = st.radio("Comparison engine", ["Keyword · no model download", "AI · Sentence Transformers"], key="engine")
    mode = "semantic" if engine.startswith("AI") else "keyword"
    st.caption("AI mode downloads a pretrained model on first use. Keyword mode compares word usage using TF-IDF.")
    custom = st.text_area("Extra skills to check", placeholder="Figma, SAP, Oracle SCM", height=90,
                          help="Comma-separated terms supplement the built-in skill catalog.")
    st.divider()
    st.markdown("**Your documents**")
    st.caption("This app processes documents in server memory without saving uploads. If hosted, documents reach that server. Clear the session when finished.")
    if st.button("Clear session", width="stretch"):
        for key in list(st.session_state):
            del st.session_state[key]
        st.rerun()

st.markdown('<div class="eyebrow">PORTFOLIO PROJECT / NLP + CAREER TOOLS</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Find your fit.<br>Build your next skill.</div>', unsafe_allow_html=True)
st.markdown('<p class="intro">Compare your resume with a job description. See the skills you mention, the gaps to review, and the evidence behind every result.</p>', unsafe_allow_html=True)
st.caption("01  ADD YOUR RESUME     →     02  ADD THE ROLE     →     03  EXPLORE THE MATCH")
st.write("")

if st.button("Try a sample analysis", type="secondary"):
    st.session_state["source"] = "Paste text"
    st.session_state["job_source"] = "Paste text"
    st.session_state["resume_text"] = (ROOT / "samples/resume.txt").read_text()
    st.session_state["job_text"] = (ROOT / "samples/job_description.txt").read_text()
    st.session_state.pop("result", None)
    st.session_state["required_years"] = None
    st.session_state["required_qualifications"] = ""
    st.session_state["required_grad_years"] = ""
    st.session_state["include_internships"] = False
    st.session_state['relevant_skills'] = ''
    st.session_state['degree_subjects'] = ''
    st.session_state.pop("requirement_source", None)
    st.session_state.pop("preview_source", None)

left, right = st.columns(2, gap="large")
with left:
    st.subheader("01 / Your resume")
    source = st.radio("Resume source", ["Paste text", "Upload file"], horizontal=True, key="source")
    uploaded_text = ""
    upload_error = False
    if source == "Upload file":
        uploaded = st.file_uploader("PDF, DOCX or TXT · up to 5 MB", type=["pdf", "docx", "txt"], key="upload")
        if uploaded:
            try:
                uploaded_text = extract_text(uploaded.getvalue(), uploaded.name)
                st.success(f"Extracted {len(uploaded_text):,} characters")
                with st.expander("Review extracted text"):
                    st.text(uploaded_text)
            except ValueError as exc:
                st.error(str(exc))
                upload_error = True
        resume = uploaded_text
    else:
        resume = st.text_area("Resume text", key="resume_text", height=270,
                              placeholder="Paste your skills, projects, experience and education…", max_chars=60000)
with right:
    st.subheader("02 / The opportunity")
    job_source = st.radio("Job description source", ["Paste text", "Upload file"],
                          horizontal=True, key="job_source")
    job_upload_error = False
    if job_source == "Upload file":
        job = ""
        job_upload = st.file_uploader("Upload job description · PDF, DOCX or TXT · up to 5 MB",
                                     type=["pdf", "docx", "txt"], key="job_upload")
        if job_upload:
            try:
                job = extract_text(job_upload.getvalue(), job_upload.name)
                st.success(f"Extracted {len(job):,} characters from job description")
                with st.expander("Review extracted job description"):
                    st.text(job)
            except ValueError as exc:
                st.error(str(exc))
                job_upload_error = True
    else:
        job = st.text_area("Job description", key="job_text", height=270,
                           placeholder="Type or paste the responsibilities and required / preferred skills…", max_chars=60000)

original_resume, original_job = resume, job
preview_source = (resume, job, source, job_source)
if st.session_state.get('preview_source') != preview_source:
    st.session_state['preview_resume'] = resume
    st.session_state['preview_job'] = job
    st.session_state['preview_source'] = preview_source
    st.session_state['edit_preview'] = False
extra = tuple(s.strip() for s in custom.split(',') if s.strip())
with st.expander('Review and correct extracted details', expanded=True):
    st.caption('Check the detected details before analysis. Correct text extraction mistakes or truthful omissions in the editable copies below. Changing an original document resets these copies.')
    editing = st.checkbox('Edit extracted resume and JD text', key='edit_preview',
                          disabled=upload_error or job_upload_error)
    if editing:
        if st.button('Reset preview to original documents'):
            st.session_state['preview_resume'] = original_resume
            st.session_state['preview_job'] = original_job
        edit_left, edit_right = st.columns(2)
        resume = edit_left.text_area('Resume text used for analysis', key='preview_resume', height=240, max_chars=60000,
                                    help='Correct skills, work experience, qualifications and graduation dates here. Keep the full document and section headings.')
        job = edit_right.text_area('JD text used for analysis', key='preview_job', height=240, max_chars=60000,
                                  help='Correct extracted JD text, including required/preferred skill headings. Keep the employer requirements faithful to the source.')
        st.caption('These copies are used for scores, evidence and reports. The uploaded files remain unchanged. Turn editing off to use the originals.')
    if resume.strip() or job.strip():
        preview_left, preview_right = st.columns(2)
        with preview_left:
            st.markdown('**Detected resume skills**')
            detected_resume = skill_context(resume, extra)
            if detected_resume:
                st.dataframe([{'Skill': s, 'Context': e['status'], 'Evidence': e['evidence']} for s, e in detected_resume.items()], hide_index=True, width='stretch')
            else:
                st.caption('No skills detected. Check the text or add Extra skills to check in the sidebar.')
            experience = experience_evidence(resume, st.session_state.get('include_internships', False))
            st.write('**Experience:** ' + ('Not found' if experience['minimum_years'] is None else f"{experience['minimum_years']:.2f} years (minimum detected)"))
            st.caption('Status: ' + experience['status'] + ' · ' + experience['method'])
            for evidence in experience['evidence']:
                st.text(evidence)
            education = education_evidence(resume, make_requirements(qualifications=st.session_state.get('required_qualifications', ''))['accepted_qualifications'])
            st.markdown('**Qualifications and pass-out years**')
            if education:
                st.dataframe(education, hide_index=True, width='stretch')
            else:
                st.caption('Not found. Use an Education heading with the qualification and graduation year together.')
        with preview_right:
            st.markdown('**Detected JD skills and priorities**')
            detected_job = skill_context(job, extra, job=True)
            if detected_job:
                st.dataframe([{'Skill': s, 'Priority': e['status'], 'Evidence': e['evidence']} for s, e in detected_job.items()], hide_index=True, width='stretch')
            else:
                st.caption('No skills detected. Check the text or add Extra skills to check in the sidebar.')
            suggested_preview = suggest_requirements(job)
            st.write('**Suggested experience minimum:** ' + (str(suggested_preview['minimum_years']) + ' years' if suggested_preview['minimum_years'] is not None else 'Not specified / not detected'))
            st.write('**Suggested qualifications:** ' + (suggested_preview['qualifications'] or 'Not specified / not detected'))
            st.write('**Suggested batches:** ' + (suggested_preview['graduation_years'] or 'No restriction detected'))
            st.caption('Review and apply JD requirements using the controls below. These suggestions are not automatically accepted.')

st.markdown("#### Mandatory JD requirements")
st.caption("Set these from the JD. The resume must state work experience, a qualification and its pass-out year. Use 0 years when freshers are allowed.")
if st.button("Read requirements from JD", disabled=not job.strip() or job_upload_error):
    suggested = suggest_requirements(job)
    st.session_state["required_years"] = suggested["minimum_years"]
    st.session_state["required_qualifications"] = suggested["qualifications"]
    st.session_state["required_grad_years"] = suggested["graduation_years"]
    st.session_state["requirement_source"] = job
    st.info("Suggested values were copied from the JD. Review them below; complex wording and equivalence clauses may need manual correction.")
req1, req2, req3 = st.columns(3)
required_years = req1.number_input("Minimum experience required (years)", min_value=0.0, max_value=60.0,
                                 value=None, step=0.5, placeholder="e.g. 2; 0 for freshers", key="required_years")
required_qualifications = req2.text_input("Accepted qualifications (any one)", placeholder="B.Tech, B.E., B.Sc",
                                        key="required_qualifications", help="Comma-separated alternatives from the JD. Use Bachelor's degree for any recognized bachelor's qualification. Specific degree titles can also be entered.")
required_grad_years = req3.text_input("Allowed pass-out years (if JD restricts)", placeholder="e.g. 2023-2026",
                                    key="required_grad_years", help="Leave blank only if the JD allows any batch. A pass-out year is still mandatory in the resume.")
include_internships = st.checkbox("Count internship experience when the JD accepts it", key="include_internships")
focus_col, subject_col = st.columns(2)
relevant_skills = focus_col.text_input('Skills requiring relevant work experience', key='relevant_skills', placeholder='e.g. Python, SQL',
    help='Optional JD restriction. Each listed skill must have an explicit duration meeting the minimum experience above. Overall tenure does not prove relevant experience.')
degree_subjects = subject_col.text_input('Accepted degree subjects (any one)', key='degree_subjects', placeholder='e.g. Computer Science, Information Technology',
    help='Optional JD restriction. The subject must appear beside an accepted degree. Leave blank when the JD has no subject restriction.')
if st.session_state.get("requirement_source") not in (None, job):
    st.warning("The JD changed after reading its requirements. Update the fields or read the requirements again.")
requirements_error = False
try:
    requirements = make_requirements(required_years, required_qualifications, required_grad_years, include_internships, relevant_skills, degree_subjects)
except ValueError as exc:
    st.error(str(exc))
    requirements_error = True
    requirements = None
if required_years is None or not required_qualifications.strip():
    st.caption("Set the experience minimum and accepted qualifications to complete the mandatory checks. You can still analyze skills; unspecified requirements will be marked Needs review.")

extra = tuple(s.strip() for s in custom.split(",") if s.strip())
signature = (resume, job, mode, extra, source, job_source, required_years, required_qualifications, required_grad_years, include_internships, original_resume, original_job, relevant_skills, degree_subjects)
already_analyzed = bool(st.session_state.get("result")) and signature == st.session_state.get("signature")
if st.button("Analyze my match →", type="primary", width="stretch",
             disabled=already_analyzed or upload_error or job_upload_error or requirements_error):
    st.session_state.pop("result", None)
    st.session_state.pop("pdf_report", None)
    if not upload_error and not job_upload_error:
        try:
            with st.spinner("Comparing documents and checking skill evidence…"):
                result = analyze(resume, job, mode, extra, requirements=requirements)
                changed = [name for name, before, after in [('resume', original_resume, resume), ('JD', original_job, job)] if before != after]
                result['input_review'] = {'corrected_documents': changed,
                    'note': 'Analysis uses user-corrected preview text for: ' + ', '.join(changed) + '. Corrections are user supplied, not independently verified.' if changed else 'Analysis uses the supplied document text without preview corrections.'}
                result['summary'] = report_summary(result)
            st.session_state["result"] = result
            st.session_state["signature"] = signature
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("The analysis engine could not start. For AI mode, install requirements-ai.txt and allow the first model download. You can select Keyword mode and try again.")

result = st.session_state.get("result")
if result and signature != st.session_state.get("signature"):
    st.info("Your inputs or engine changed. Analyze again to update the report.")
    result = None

if result:
    st.success("Analysis complete. Change your resume, job description, engine or extra skills to analyze again.")
    st.divider()
    st.subheader("03 / Your match, explained")
    summary = report_summary(result)
    st.markdown('### At a glance')
    st.write('**Result: ' + summary['status'] + '**')
    st.write(f"**Matched skills:** {summary['matched_count']} of {summary['job_skill_count']} — " + (', '.join(result['matched_skills']) or 'None detected'))
    st.write('**Missing required skill evidence:** ' + (', '.join(summary['required_gaps']) or 'None detected'))
    st.write('**Missing JD settings:** ' + (', '.join(summary['missing_jd_settings']) or 'None'))
    st.write('**Missing resume details:** ' + (', '.join(summary['missing_resume_details']) or 'None'))
    st.markdown('#### Your next three actions')
    for index, action in enumerate(summary['top_actions'], 1):
        st.write(f'{index}. {action}')
    st.caption(summary['score_explanation'])
    st.caption(summary['note'])
    st.caption(summary['input_note'])
    review = result["requirement_review"]
    if review["summary"] == "Meets configured checks":
        st.success("Mandatory resume details: meets the configured checks.")
    elif review["summary"] == "Does not meet configured checks":
        st.error("Mandatory resume details: one or more configured requirements are not met. Review the reasons below.")
    else:
        st.warning("Mandatory resume details: needs review. Missing or unclear information cannot pass these checks.")
    for check in review["checks"]:
        status_label = {"met": "Meets setting", "not_met": "Does not meet setting", "missing": "Required detail missing", "review": "Needs review"}[check["status"]]
        st.write(f"**{check['requirement']}: {status_label}** — {check['observed']}")
        if check["status"] != "met":
            st.caption(check["action"])
    with st.expander("Requirement settings and resume evidence"):
        for check in review["checks"]:
            st.write(check["requirement"] + " / JD setting: " + check["expected"])
            st.text(check["evidence"] or "No supporting resume text found.")
        st.caption("Experience method: " + review["experience"]["method"])
        for note in review["experience"]["notes"]:
            st.caption(note)
        st.caption(review["note"])
    a, b, c = st.columns(3)
    a.metric("AI text similarity" if mode == "semantic" else "Keyword text similarity", f"{result['text_similarity']} / 100")
    coverage = result["skill_coverage"]
    b.metric("Detected skill coverage", "N/A" if coverage is None else f"{coverage}%")
    c.metric("Job skills to review", len(result["skills_not_found"]))
    st.caption("Text similarity is not a hiring probability or an ATS score. Overall coverage counts positive resume mentions across all detected job skills equally. Learning and negative/conflicting mentions do not count as positive evidence.")
    priority_columns = st.columns(3)
    for column, priority in zip(priority_columns, ("required", "preferred", "unspecified")):
        value = result[priority + "_coverage"]
        column.metric(priority.title() + " skill coverage", "N/A" if value is None else f"{value}%")
    st.caption("Priority is inferred from explicit wording and section headings. Unmarked skills stay unspecified; review the Evidence tab for mistakes.")
    result = dict(result)
    skills_tab, evidence_tab, plan_tab, notes_tab = st.tabs(["Skills overview", "Evidence", "Action plan", "How to read this"])
    with skills_tab:
        x, y = st.columns(2)
        with x:
            st.markdown("#### ✓ Mentioned in both")
            st.write(" · ".join(result["matched_skills"]) or "No matching catalog skills detected.")
        with y:
            st.markdown("#### + Without positive resume evidence")
            st.write(" · ".join(result["skills_not_found"]) or "No missing catalog skills detected.")
        st.markdown("#### Other resume skills")
        st.write(" · ".join(result["additional_skills"]) or "None detected.")
        for priority in ("required", "unspecified", "preferred"):
            st.markdown(f"#### {priority.title()} skills to review")
            st.write(" · ".join(result["missing_by_priority"][priority]) or "None detected.")
        st.info("A skill not found in your resume may still be a skill you have. Check the evidence before editing your resume.")
    with evidence_tab:
        if result["evidence"]:
            st.dataframe(result["evidence"], hide_index=True, width="stretch")
        else:
            st.info("No job skills detected. Add custom skills in the sidebar.")
        st.caption("Evidence excerpts are limited to 500 characters. Context rules are approximate; a mention does not verify proficiency.")
        with st.expander("Review all resume mentions and context"):
            for skill, entry in result["resume_context"].items():
                st.write(f"{skill} — {entry['status']}")
                for mention in entry["mentions"]:
                    st.text(f"{mention['status']}: {mention['evidence']}")
        if result["excluded_job_skills"]:
            with st.expander("Job skills marked as not required"):
                for skill, entry in result["excluded_job_skills"].items():
                    st.write(f"{skill}: {entry['evidence']}")
    with plan_tab:
        st.subheader("Daily study plan")
        st.write("Build a starter routine for JD skills without positive resume evidence. Required skills come first.")
        restored = None
        with st.expander('Save or restore progress across sessions'):
            st.caption('Download a progress backup below before closing the app. Next time, analyze the same documents, upload the backup and click Restore progress. The backup contains levels and completed days, not your resume/JD text. Keep it private if custom skill names are sensitive.')
            backup = st.file_uploader('Upload progress backup (JSON, up to 100 KB)', type=['json'], key='progress_backup')
            if st.button('Restore progress', disabled=backup is None):
                try:
                    restored = import_progress(backup.getvalue(), result['learning_plan'])
                    st.session_state['plan_days'] = restored['requested_days']
                    st.session_state['plan_minutes'] = restored['minutes_per_day']
                    for skill, level in restored['levels'].items():
                        st.session_state['level_' + skill] = level
                    restored_id = plan_key(restored)
                    st.session_state['study_progress_' + restored_id] = {day: True for day in restored['completed_days']}
                    for day in range(1, restored['total_days'] + 1):
                        st.session_state[f'done_{restored_id}_{day}'] = day in restored['completed_days']
                    st.success('Progress restored. Study settings and completed days have been recovered.')
                except ValueError as exc:
                    st.error(str(exc))
        levels = {}
        with st.expander('Personalize your skill levels'):
            st.caption('Beginner includes all foundations. Intermediate skips two introductory topics. Advanced focuses on project and review challenges. These are self-assessed levels; choose Beginner if prerequisites are unfamiliar.')
            for step in result['learning_plan']:
                skill = step['skill']
                levels[skill] = st.selectbox(skill + ' level', LEVELS, key='level_' + skill)
        plan_left, plan_right = st.columns(2)
        st.session_state.setdefault('plan_days', 14)
        st.session_state.setdefault('plan_minutes', 60)
        requested_days = plan_left.selectbox("Preferred plan length (days)", [7, 14, 30], key="plan_days")
        daily_minutes = plan_right.selectbox("Daily study budget (minutes)", [30, 60, 90, 120], key="plan_minutes")
        daily = build_daily_plan(result["learning_plan"], requested_days, daily_minutes, levels)
        result["daily_plan"] = daily
        plan_id = plan_key(daily)
        if not daily["days"]:
            st.success("No study tasks are needed for the detected skill gaps. Review your evidence and keep practicing.")
        else:
            st.caption(f"{len(daily['skills'])} skills · {daily['starter_sessions']} starter sessions · {daily['total_days']} scheduled days · up to {daily_minutes} minutes/day")
            if daily["extended"]:
                st.info(f"Your selected budget needs {daily['total_days']} days to include every starter topic. The schedule was extended from {requested_days} days; increase your daily budget for a shorter plan.")
            st.caption(daily["note"])
            selected_day = st.selectbox("Choose study day", list(range(1, daily["total_days"] + 1)),
                                        format_func=lambda value: f"Day {value}", key="study_day_" + plan_id)
            day = daily["days"][selected_day - 1]
            st.markdown(f"#### Day {selected_day} · {day['minutes']} minutes scheduled")
            for session_index, session in enumerate(day["sessions"]):
                st.markdown(f"**{session['skill']} / {session['topic']}**")
                st.caption(f"{session['priority'].title()} · {session['curriculum']} · 10 min learn + 15 min practice + 5 min review")
                st.write(session["goal"])
                st.caption('Level: ' + session['level'] + ' · Prerequisites: ' + session['prerequisite'])
                st.write('Short lesson: ' + session['lesson'])
                st.write('Challenge: ' + session['challenge'])
                st.write("Practice: " + session["practice"])
                st.write("Check: " + session["check"])
                with st.expander('Topic self-check: ' + session['topic']):
                    st.write(session['topic_question'])
                    for item in session['rubric']:
                        st.write('• ' + item)
                    quiz = session.get('quiz')
                    if quiz:
                        quiz_id = f'{plan_id}_{selected_day}_{session_index}'
                        answer = st.radio(quiz['question'], quiz['options'], index=None, key='quiz_' + quiz_id)
                        if st.button('Check answer', key='check_quiz_' + quiz_id):
                            if answer is None:
                                st.info('Choose an answer first.')
                            elif answer == quiz['options'][quiz['answer']]:
                                st.success('Correct. ' + quiz['explanation'])
                            else:
                                st.warning('Try the lesson again. ' + quiz['explanation'])
                    else:
                        st.caption('Open-ended self-check: use the rubric to review your work; it is not automatically graded.')
                for resource in session["resources"]:
                    st.link_button(resource["kind"].title() + ": " + resource["title"], resource["url"])
                    if not resource["curated"]:
                        st.caption("Search results have not been reviewed. Choose a lesson matching today's topic and your level.")
            progress_key = "study_progress_" + plan_id
            progress = dict(st.session_state.get(progress_key, {}))
            done_key = f'done_{plan_id}_{selected_day}'
            st.session_state.setdefault(done_key, progress.get(selected_day, False))
            progress[selected_day] = st.checkbox("I finished today's practice and self-check",
                                                key=done_key)
            st.session_state[progress_key] = progress
            daily["completed_days"] = [d["day"] for d in daily["days"] if progress.get(d["day"], False)]
            st.download_button('Save progress backup', export_progress(daily), 'skillbridge_progress.json', 'application/json')
            st.progress(len(daily["completed_days"]) / daily["total_days"], text=f"{len(daily['completed_days'])} of {daily['total_days']} days completed in this session")
            st.caption("Completing a day does not change your resume match score. Downloads include the selected schedule and completion status.")
            with st.expander("See the complete daily schedule"):
                st.dataframe([{"Day": d["day"], "Minutes": d["minutes"],
                               "Topics": " | ".join(s["skill"] + ": " + s["topic"] for s in d["sessions"])} for d in daily["days"]], hide_index=True, width="stretch")
        st.divider()
        st.markdown("#### Suggestions and skill practice details")
        for item in result["suggestions"]:
            st.write("• " + item)
        for step in result["learning_plan"]:
            with st.expander(step["priority"].title() + " / Practice " + step["skill"]):
                st.write(step["goal"])
                st.write(step["practice"])
                st.write("Check your work: " + step["check"])
                st.caption(step["proof"])
                if step["resource_url"]:
                    st.link_button(step["resource_title"], step["resource_url"])
                else:
                    st.caption(step["resource_note"])
    with notes_tab:
        st.write("Engine: " + result["model"])
        for item in result["limitations"]:
            st.write("• " + item)
        st.write("AI mode averages token-length-weighted chunk embeddings, then computes cosine similarity. Keyword mode uses TF-IDF and cosine similarity. Neither mode trains on your documents.")
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download readable report", markdown_report(result), "job_match_report.md", "text/markdown", width="stretch")
    d2.download_button("Download JSON report", json.dumps(result, indent=2, ensure_ascii=False), "job_match_report.json", "application/json", width="stretch")
    try:
        pdf_signature = (signature, requested_days, daily_minutes, tuple(sorted(levels.items())), tuple(daily["completed_days"]))
        if "pdf_report" not in st.session_state or st.session_state.get("pdf_signature") != pdf_signature:
            st.session_state["pdf_report"] = pdf_report(result)
            st.session_state["pdf_signature"] = pdf_signature
        d3.download_button("Download PDF report", st.session_state["pdf_report"], "job_match_report.pdf", "application/pdf", width="stretch")
    except Exception:
        d3.error("PDF export could not be created. Reinstall requirements.txt; Markdown and JSON downloads remain available.")
    st.caption("Reports contain skill evidence quoted from your documents. Review them before sharing.")
else:
    st.divider()
    st.caption("READY WHEN YOU ARE • Try the sample or add your own documents above.")
