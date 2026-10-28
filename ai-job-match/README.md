# SkillBridge — AI Job Match & Skill Gap Analyzer

A Python + Streamlit portfolio application that compares a resume with a job description and explains its results. Includes a pretrained Sentence Transformers engine and an independent TF-IDF keyword mode.

## Features

- Evaluate extraction with a reproducible multi-role synthetic benchmark, per-case disagreements and a documented independent human-review protocol.
- Check explicitly stated skill-specific experience and subjects beside accepted degrees, using optional JD restrictions.
- Personalize each missing skill as Beginner, Intermediate or Advanced, with short lessons, challenges and formative quizzes.
- Save a portable progress backup and restore completed days and levels in a later session.
- Review detected skills, experience, qualifications and graduation years before analysis; edit extracted resume/JD text in a preview copy.
- Read a shared At a glance summary in the app and exports, with missing settings separated from missing resume details and three next actions.
- Paste a resume or upload PDF, DOCX or UTF-8 TXT (5 MB limit).
- Type/paste a job description or upload PDF, DOCX or UTF-8 TXT, then choose the comparison engine.
- Configure mandatory experience, qualification and pass-out-year checks; use **Read requirements from JD** for editable suggestions.
- View text similarity and detected skill coverage as separate measures.
- See positive skill mentions, skills without positive resume evidence, and other resume skills.
- Distinguish learning goals, negative statements and conflicting mentions using English rules.
- Separate required, preferred and unspecified job skills, with category coverage and evidence.
- Inspect the original text evidence behind each detected job skill.
- Add comma-separated custom skills without editing code.
- Receive prioritized practice tasks, checks and curated learning links for selected skills; other skills have a labeled fallback.
- Generate a daily study schedule for every detected skill gap, with beginner topics, exercises, video links and reading.
- Choose 7/14/30 days and a 30/60/90/120-minute daily budget; track completed days in the session.
- Download PDF, Markdown and JSON reports.
- Use fictional samples to demonstrate the app without sharing personal data.
- Clear session data and prevent stale reports after changing inputs.
- After a successful analysis, the Analyze button is disabled until inputs or settings change.
- Automated logic, extraction and Streamlit flow tests; GitHub Actions workflow.

## Requirements

Python 3.11 or 3.12 recommended. A CPU is sufficient. AI mode requires internet access for the initial model download; downloaded model weights are cached by Hugging Face. No OpenAI API key or paid service is required. Python dependencies also require an internet connection to install.

## Start on Windows

Extract this ZIP. Open the `ai-job-match` folder in VS Code, then open its terminal:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Using the virtual environment's Python directly avoids PowerShell activation-policy problems. Open the local URL printed in the terminal, normally `http://localhost:8501`.

For a lighter installation with keyword analysis only, replace `requirements-ai.txt` with `requirements.txt`. To add AI later, run the AI installation command.

### Updating an existing copy

Stop the running app with Ctrl+C. Extract this updated package into a new folder and open its `ai-job-match` folder in VS Code. Follow the commands above to create its environment and install its dependencies. Replace the complete project, not only `app.py`: this version adds context, action-plan and PDF modules. If updating files in an existing installation, rerun `.venv\Scripts\python.exe -m pip install -r requirements-ai.txt` before restarting.

## Start on macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-ai.txt
.venv/bin/python -m streamlit run app.py
```

## First demonstration

1. Keep **Keyword** selected for an immediate demo.
2. Click **Try a sample analysis**.
3. Click **Analyze my match**.
4. The sample has four matching skills and five job skills not found, giving **44.4% skill coverage**.
5. Open Evidence and Action plan; download a report.
6. Select **AI · Sentence Transformers** and analyze again to use the pretrained model. The first use may take several minutes to download and load.

The sample includes Python, SQL, Pandas and Git in both documents. Excel, Data Visualization, Statistics, Power BI and Communication are present only in the sample job description. Text similarity varies by engine and is deliberately not combined with skill coverage.

The sample has **50.0% required coverage** (3 of 6) and **33.3% preferred coverage** (1 of 3). Unspecified coverage is N/A because the sample labels every detected job skill. A sample PDF is included at `output/pdf/sample_job_match_report.pdf`.

## Review extracted details and report summary

After adding the documents, open **Review and correct extracted details**. It shows skill context and JD priorities with evidence, resume experience, qualifications and pass-out years, plus suggested JD requirements. Enable **Edit extracted resume and JD text** to correct the editable document copies. Keep the full text and headings; correct only extraction mistakes or truthful omissions. For example, place a graduation year beside its qualification, or fix a garbled skill name. Use **Extra skills to check** for terms outside the catalog. These edits are text corrections, not direct overrides of the matching rules; check the updated preview to confirm the intended interpretation.

Use **Read requirements from JD** to populate the requirement controls from the corrected JD, then review the settings and analyze. Corrected text is used consistently for similarity, skill matching, mandatory checks, evidence and learning plans. Reports identify which documents had preview corrections. Originals remain unchanged; reset restores them, turning editing off uses the originals, and replacing either source document resets both copies. Changes invalidate displayed results until reanalysis. Copies and corrections are session-only.

**At a glance** shows the comparison status, matched skills, missing required skill evidence, missing JD configuration, missing resume details and three prioritized actions. A separate explanation distinguishes text similarity from skill coverage. The PDF starts with this overview and then provides detailed evidence and the plan; unusually long custom terms/actions can extend the overview. JSON includes structured `summary` and, for app analyses, `input_review` fields. No hiring-eligibility threshold is implied.

## Daily study planner

After analysis, open **Action plan**. Select your preferred plan length and daily study budget, then choose a day. Each session suggests 10 minutes watching/reading, 15 minutes practicing and 5 minutes reviewing. Pause long videos when the learning budget runs out; continue next time as needed.

The planner uses skills requested in the JD that lack positive resume evidence, including skills marked learning or needing context review. Required gaps come first, followed by unspecified and preferred gaps. It does not schedule unrelated resume skills. If you already know a skill, review the evidence and correct the resume instead of treating the plan as proof you lack it.

Ten common skills have four curated starter topics, followed by a mini-project and a self-check. Other catalog/custom skills get a visibly labeled generic starter template. This is not an exhaustive syllabus or a promise of mastery. Every gap receives tasks. If the selected budget is too short, the app extends the schedule rather than silently dropping topics. Longer plans use reinforcement days after the starter tasks. The daily budget is a maximum; some days use less time.

The sample has five gaps and thirty 30-minute sessions. At 60 minutes/day, the default 14-day preference is extended to **15 days**. Increasing the budget to 90 minutes/day allows the starter work to fit within the selected 14 days.

Selected skills have curated video/course links. All topics also have clearly labeled YouTube searches; skills without curated reading get a reading search. Search results are not reviewed or endorsed. Curated resources were selected using publisher pages/metadata; complete videos were not watched or audited. Some tutorials are older, so software interfaces may differ. The SQL video uses the SQL Server T-SQL dialect; the reading reference uses PostgreSQL.

Tick the daily completion box after doing the exercise and self-check. Click **Save progress backup** before closing the app. In a later session, analyze the same documents, open **Save or restore progress across sessions**, upload that JSON and click **Restore progress**. This restores plan settings, skill levels and completed days. It is a manual portable save, not automatic server storage. New sessions and Clear session discard unsaved progress. A backup from different gaps, priorities or a changed curriculum is rejected. Backups contain settings, skill names, a plan fingerprint and completed days, not resume/JD text; custom skill names can still be sensitive. Quiz answers are practice-only and are not saved. Changing study settings creates a separate plan without reanalysis. Progress never increases skill coverage.

In **Personalize your skill levels**, Beginner schedules all six sessions per skill; Intermediate skips the first two introductory topics; Advanced focuses on mini-project and review with harder challenges. Prerequisites remain visible. Ten skills have forty authored topic lessons and ten formative multiple-choice quizzes, plus topic-specific open-ended self-check rubrics. Other skills retain an explicitly generic curriculum. Levels are self-assessed, and quiz success is not proof of proficiency. The suggested session budget may need extending for harder work. PDF/Markdown/JSON exports include levels, lessons and quiz answer explanations; the app shows feedback after checking an answer.

## Mandatory experience, qualification and graduation details

Below the resume and JD inputs, enter the **minimum experience required**, **accepted qualifications** (comma-separated alternatives), and **allowed pass-out years** if the JD restricts batches. For example: `2`, `B.Tech, B.E., B.Sc`, and `2023-2026`. A spinner changes the years; use `0` when freshers are allowed. **Read requirements from JD** suggests values for common wording. Review all suggested values, especially required/preferred qualifications, equivalent-experience clauses and requirements tied to a particular skill. Missing JD requirements remain blank instead of being invented.

All three resume details are mandatory for the new checks to pass. An omitted work-experience statement is flagged as missing, not treated as zero. A fresher can explicitly write `Work experience: 0 years`. Experience can also be estimated from month/year date ranges under a Work Experience heading; overlapping periods count once. Internships are excluded unless you select the option accepting them. Year-only dates, future/reversed work dates and conflicting totals require review. Month-based totals do not verify relevance or employment type.

Qualifications recognize common degree names and aliases. `Bachelor's degree` accepts the recognized bachelor's categories; a specific degree such as `B.Tech` requires that category. Other qualification titles can be entered and matched literally. Higher qualifications are not automatically treated as equivalents. Expected or incomplete degrees are flagged rather than treated as completed qualifications.

If the JD restricts specialization, fill **Accepted degree subjects (any one)**. Common subject aliases such as CS/CSE are recognized; the subject must be beside an accepted qualification, and a batch restriction must match that same qualification. Missing or ambiguous subjects require review; a clearly different recognized subject does not pass. Unknown subjects use literal matching. Related-field clauses, degree equivalence and credentials still require manual review.

If the JD requires experience with specific skills, fill **Skills requiring relevant work experience**. Each comma-separated skill uses the minimum years configured above. The app accepts explicit scoped claims such as `Python experience: 2 years` or `2 years of experience with Python`; a general employment total, skill-list mention or project does not establish that duration. Conflicting claims, unsupported wording, unaccepted internships and unclear bounds require review. Different per-skill minimums, relevance inferred from job duties and employer verification are not supported. These optional restrictions are entered by the user, not auto-accepted from JD suggestions.

The pass-out year must appear beside the relevant education entry. Birth dates and employment dates are not used as graduation evidence. Leave the JD year filter blank only if any batch is allowed: the resume still needs its graduation year. Future completion dates need review.

The outcome is **Meets configured checks**, **Does not meet configured checks**, or **Needs review**, with evidence and an action for each row. Missing details or unconfigured experience/qualification requirements cannot clear these checks even with 100% skill coverage. These are document checks, not verified credentials or a final hiring decision. The skill percentage remains a separate measure; no 60%/70% acceptance threshold has been selected. Changing a requirement invalidates the old report. All exports include the settings and evidence.

The original fictional sample intentionally has no stated work-experience total or pass-out year. It therefore shows **Needs review** in this section while retaining 44.4% skill coverage. To try a passing example, use the fictional inputs in `samples/requirements_resume.txt` and `samples/requirements_job.txt`, click **Read requirements from JD**, then analyze.

## Accuracy benchmark

Run `python evaluate.py`. The included 16 synthetic cases cover multiple roles and edge cases. See `evaluation/README.md` for the label schema and human-review protocol, and `evaluation/latest_results.json` for metrics and disagreements. `baseline_results.json` preserves the pre-fix result: 15/16 exact cases, with a missing canonical Testing name. After the fix, all 16 development cases and 8 labeled requirement checks agree with their expected labels. **Zero cases have independent human review**; these results are not a real-world accuracy estimate. They evaluate text rules, not document layout extraction, semantic ranking, learning outcomes or hiring suitability. Add independently labeled, consented and anonymized held-out examples before making an accuracy claim.

Lesson references checked for this update include [Python functions](https://docs.python.org/3/tutorial/controlflow.html), [PostgreSQL SELECT and HAVING](https://www.postgresql.org/docs/current/sql-select.html), and [Git revert](https://git-scm.com/docs/git-revert). Lessons and quizzes are authored teaching aids; linked resources remain separate publisher material.

## How the scoring works

### Semantic engine

`sentence-transformers/all-MiniLM-L6-v2` converts text into embeddings. Text is split using the model tokenizer into chunks within its configured input length. Each chunk is embedded. A token-count-weighted mean represents each document. Cosine similarity compares the two document vectors. The display clips negative cosine values to zero and multiplies by 100.

This is a document-similarity heuristic. It has not been calibrated against hiring outcomes. Averaging can hide individual requirements, so review skill evidence separately.

### Keyword engine

TF-IDF represents each document using word unigrams and bigrams, then cosine similarity compares those vectors. It measures lexical overlap, not semantic understanding. It is clearly labeled in the interface and never silently substitutes for the AI engine.

### Skill coverage

`job skills with positive resume evidence / all active detected job skills × 100`

The denominator includes only catalog or custom skills. Skills explicitly classified as not required are excluded. Overall coverage is unweighted; required, preferred and unspecified categories also have separate coverage scores. An empty denominator displays N/A. Priority rules use explicit cues and headings; unmarked skills remain unspecified. When a skill has several priority labels, required takes precedence over unspecified and preferred.

Resume context rules distinguish positive mentions, learning goals, explicit negatives and conflicting positive/negative statements. Only positive mentions count toward coverage. Conflicts are flagged for review; all supporting mentions are available in Evidence and structured exports. This is approximate English rule matching, not a verified proficiency assessment. Whole-document similarity still uses the full input text, including negative statements.

### Suggestions

Suggestions and learning plans are rule-based templates. Required gaps come first, followed by unspecified and preferred gaps. Curated entries contain a concrete exercise, checks and a portfolio outcome. Selected skills link to primary learning resources; other skills explicitly say no curated link is available. These plans do not invent experience or certifications and are not generated by an LLM.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface, session state and report downloads |
| `analyzer/extraction.py` | In-memory PDF, DOCX and text extraction |
| `analyzer/core.py` | Skill extraction, both engines, coverage and report generation |
| `analyzer/context.py` | English context and requirement-priority rules |
| `analyzer/plans.py` | Practice catalog, beginner topics, video/reading links and time-budgeted daily scheduling |
| `analyzer/reports.py` | In-memory, paginated PDF report export |
| `analyzer/requirements.py` | Mandatory resume-detail checks and editable JD requirement suggestions |
| `data/skills.json` | Editable skill names and aliases |
| `samples/` | Fictional resume and job description |
| `tests/` | Logic, parser and interface tests |
| `.streamlit/config.toml` | Theme, upload limit and telemetry setting |
| `PROJECT_GUIDE.md` | Full beginner explanation and interview preparation |
| `VALIDATION.md` | Checks performed and testing limits |

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The normal test suite does not download a model. It tests the semantic integration using a small deterministic model double. See VALIDATION.md for whether a real model was exercised in the build environment.

## Customize and extend

Edit `data/skills.json` to add canonical names and aliases. Short aliases can be ambiguous, so use distinctive phrases where possible. Custom skills entered in the sidebar are checked in both documents. The taxonomy is cached; restart the app after editing its JSON file.

Meaningful next extensions: OCR, section-aware semantic comparison, human-labeled evaluation cases, role-specific skill catalogs, broader learning-resource coverage and more robust context parsing. Context and priority detection are currently rule-based; category scores remain separate instead of inventing a weighted overall hiring score.

## GitHub and deployment

Create an empty GitHub repository, then use VS Code Source Control to initialize this extracted folder, commit and publish to your repository. Do not include personal resumes or reports in the repository.

You can host the app on a Python host that supports Streamlit. Set the entry point to `app.py`; install `requirements-ai.txt` if enabling AI. Some hosts install only `requirements.txt` by default: configure their install command or add `sentence-transformers` to the base requirements for that deployment. Model startup and memory needs depend on the host. A hosted app processes uploaded documents on its server; review the host's data-handling terms before using real resumes. This package does not create an account, publish a repository or deploy a live website.

## Limits and data handling

- English text is the intended input. Scanned PDFs need OCR first.
- Password-protected PDFs are rejected. DOCX extraction includes paragraphs and tables; headers, footers, text boxes and complex layouts may be incomplete. Review extracted text.
- Context rules cover common English phrases and headings but can miss complex negation, mixed lists and unusual wording. Review the evidence and inferred priorities. Aliases such as R, ML and SAN can be ambiguous.
- PDF reports use a bundled Latin/Greek/Cyrillic font. Unsupported characters appear as `?`; JSON and Markdown retain original Unicode text. Reports escape markup and wrap long evidence.
- Missing text does not establish that the person lacks a skill.
- Mandatory checks compare stated experience, qualifications and graduation dates with configured requirements. They do not verify degrees, work history, relevant experience, seniority or final job eligibility.
- This app is a candidate self-review tool; its scores should not decide hiring.
- Uploaded documents are processed in memory; the app does not save them to disk or send text to an LLM API. Inputs and reports remain in the active Streamlit session until cleared or expired. Model files may be downloaded and cached; documents are not used for training.
- Report downloads contain excerpts of input documents. Clear session removes app session values; it is not a guarantee of immediate physical memory erasure.

## Primary references

- [Sentence Transformers semantic similarity](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- [SentenceTransformer model API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html)
- [Streamlit file uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)

This is an original educational portfolio implementation, not a copy of the linked recruitment platform.
