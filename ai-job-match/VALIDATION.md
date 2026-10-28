# Validation — updated 26 October 2026

## Current update

### Evaluation, relevant requirements and personalized learning

The current suite has **82 tests**. New tests cover scoped versus total experience, insufficient and ambiguous claims, internship acceptance, subject aliases and association with the accepted degree/batch, changed learning levels, portable progress round trips and wrong-plan/corrupt backups, fresh-session restore, quiz feedback, stale requirements, unchanged match scores, PDF refresh and personalized exports. Automated Streamlit AppTest flows were used; no live-browser visual audit was performed.

The 16-case synthetic development benchmark initially had 15 exact cases, matched-skill F1 0.9818 and required-skill F1 0.9877. It exposed missing canonical category-name recognition for Testing. After fixing catalog construction, all 16 cases agree exactly, with 28 matched-skill and 41 required-skill true positives and no false positives/negatives in this small development set; all 8 labeled requirement checks agree. Baseline and final results are retained. These labels were authored by the assistant, with **0 independently human-reviewed cases**. This is not a representative or held-out real-world accuracy measurement.

Regenerated the 13-page sample PDF and Markdown report with lessons and quiz answers. Rendered every PDF page and inspected wrapping, pagination, margins and footers. The PDF may span more pages because it now includes the actual learning content. Quiz answers and project rubrics are formative guidance, not a validated assessment instrument. Persistence uses explicit portable backup/restore; unsaved session changes and quiz attempts are not persisted.

### Editable preview and report summary

The suite now has **65 tests**. Eight new checks cover missing JD settings versus missing resume details, required skill gaps despite complete mandatory checks, no-skill handling, shared summary and correction provenance in exports, preview corrections affecting scores, corrected JD suggestions, qualification checks, stale-result hiding, original-text preservation, reset/toggle/source replacement, and uploaded-text corrections. AppTest verifies UI behavior; no live-browser visual review was performed. The new nine-page sample PDF was rendered and visually checked, including its overview and detailed evidence pages.

### Mandatory resume requirements

Ran `python -m unittest discover -s tests -q`: **57 tests passed**. Twenty new tests cover JD requirement suggestions, missing versus zero experience, numeric and date-based experience, overlapping employment periods, internship settings, qualification aliases, incomplete qualifications, graduation-year association and batch restrictions, invalid settings, report contents, and Streamlit controls and stale-result handling. A full skill match cannot bypass missing mandatory details.

The new fictional requirements resume/job pair passes the configured checks; the original sample correctly needs review for missing details. Regenerated the Markdown and PDF sample reports and visually inspected all eight rendered PDF pages for wrapping, margins and readable sections. AppTest checks passed; no live-browser visual review was performed. These are rule-based document checks, not credential verification or a hiring-eligibility benchmark.

### Daily study planner

The updated suite has **37 tests**. New checks cover every-gap coverage, every starter topic, daily time budgets, automatic extension, required-first ordering, reinforcement days, empty plans, invalid settings, encoded search links, labeled generic curricula, direct video links, full Markdown/PDF schedules and clickable PDF annotations. UI checks cover schedule changes without reanalysis, PDF cache refresh, completion tracking and switching between days. This planner remains a template-based starter roadmap; no learning-outcome study was performed.

The sample produces 30 starter sessions across five gaps: at 60 minutes/day its 14-day preference extends to 15 days. The sample PDF and Markdown report have been regenerated to include the schedule and resources. Rendered all seven PDF pages with Poppler and visually inspected text wrapping, daily blocks, resource links and page footers.

### Previous context and report update

Ran `python -m unittest discover -s tests -v` in the local Windows environment: **31 tests passed**.

New checks cover JD upload and sample reset, invalid-upload blocking, disabled Analyze after success and re-enabling after edits, three download controls, negative/learning/conflicting skill mentions, learning section headings, the Machine Learning name boundary, required/preferred/unspecified classifications, list suffixes, exclusion from coverage, priority ordering, custom-skill fallback and PDF/Markdown contents.

The sample remains 44.4% overall coverage, with 50.0% required coverage and 33.3% preferred coverage. PDF checks include escaped markup, long evidence, Latin accents and page footers. Generated `output/pdf/sample_job_match_report.pdf`, rendered all four pages with Poppler and visually inspected wrapping, margins, page numbers and section headings. The fictional sample Markdown report was regenerated from the current analyzer.

Streamlit UI behavior was tested with AppTest; a live browser visual review was not performed for this update. Real-model inference was not rerun: the semantic implementation is unchanged, and deterministic semantic integration checks pass. Context and priority tests are regression examples, not a measured accuracy benchmark. Unsupported PDF font characters are replaced with `?`, while Markdown and JSON retain Unicode.

The following records describe the original build and are retained as historical validation.

## Original build — 23 October 2026

### Original automated checks

`python -m unittest discover -s tests -v`

**19 tests passed.**

The suite covers:

- Fictional sample: four matched skills, five not found, nine total job skills, 44.4% coverage.
- Alias matching and boundaries for JavaScript, C++, C#, MySQL and scikit-learn.
- Custom skills, full-width Unicode text and capitalization.
- No detected job skills → N/A coverage.
- Short/empty and oversized input validation.
- Identical and unrelated keyword comparisons; empty vocabularies.
- A documented negation limitation.
- Token-aware semantic chunking using a deterministic model double.
- Explicit semantic failure instead of silent keyword fallback.
- TXT, PDF and DOCX extraction, including DOCX tables.
- Encrypted PDFs, blank/scanned PDFs, invalid files and oversized uploads.
- Streamlit sample analysis, metrics and presence of two report-download controls.
- Hiding stale reports after editing input.
- Upload interaction, input validation, session clearing and visible AI-engine failure.

### Original real pretrained-model integration

Installed Sentence Transformers and loaded `sentence-transformers/all-MiniLM-L6-v2` successfully.

On the included fictional sample:

| Output | Observed value |
|---|---|
| AI text similarity | 55.7 / 100 |
| Detected skill coverage | 44.4% |

This check used the real pretrained model, not the test double. Values can vary slightly across model/library versions. The initial environment needed a SOCKS proxy transport dependency to reach the model hub; this was an environment setup issue, not an application fallback. Normal local installations do not need proxy configuration unless their network uses one.

Reproduce the integration check after installing AI dependencies:

```bash
python verify_ai.py
```

### Original scope and limits

The application server also started successfully and returned HTTP 200 with `ok` from its local health endpoint.

The Streamlit application was exercised with AppTest. A browser screenshot review could not be completed because the browser binary download failed in the build environment. No visual screenshot approval is claimed.

The tests are functional checks. No labeled recruitment dataset, extraction-accuracy benchmark, hiring-outcome validation, accessibility audit, production load test or security audit was performed. This is a local portfolio application, not a production recruitment decision system.
