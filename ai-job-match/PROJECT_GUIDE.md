# Complete project explanation — simple English

## 1. What did we build?

We built **SkillBridge: AI Job Match & Skill Gap Analyzer**. It helps someone review their resume for a particular job. It reads the resume and job description, compares the text, checks mentioned skills and explains possible improvements.

It answers three questions:

1. How similar are these two documents?
2. Which detected job skills also appear in the resume?
3. Which detected job skills should the person review or learn?

It does not know whether a company will shortlist you.

## 2. A simple example

Imagine a job mentions Python, SQL, Excel and Power BI. Your resume mentions Python and SQL. The app shows two matching skills and two job skills not found in the resume.

Skill coverage = 2 ÷ 4 × 100 = **50%**.

This does not mean you have a 50% chance of getting the job. You may already know Excel but have forgotten to mention it. The app only sees the text you provide.

## 3. The complete journey

**Resume + job description → text extraction → text normalization → similarity comparison and skill extraction → evidence, scores and suggestions → downloadable report.**

The comparison and skill extraction are separate operations. The app does not average their scores into a single unexplained number.

## 4. What each technology does

| Technology | Simple explanation | Why we use it |
|---|---|---|
| Python | Main programming language | Connects all parts |
| Streamlit | Builds a web interface from Python | Lets users upload files and view results |
| pypdf | Reads text from PDFs | Supports PDF resumes |
| python-docx | Reads Word documents | Supports DOCX resumes |
| Sentence Transformers | A pretrained NLP model library | Represents document meaning as numbers |
| NumPy | Works with numerical arrays | Combines chunk embeddings |
| scikit-learn | Provides text and similarity tools | TF-IDF and cosine similarity |
| JSON | Stores structured data | Skill catalog and report export |
| unittest + AppTest | Automated checking tools | Tests logic and the user flow |
| GitHub Actions | Runs checks on repository changes | Helps maintain the project |

There is no separate Angular or React frontend. Streamlit provides the frontend and runs the Python logic. No database is required because the app does not keep user accounts or analysis history.

## 5. Resume extraction

`analyzer/extraction.py` receives the uploaded file as bytes. Bytes are the raw contents of a file.

- TXT: decode UTF-8 text.
- PDF: extract text from each page using pypdf.
- DOCX: read paragraphs and table cells using python-docx.

The function rejects empty files, unsupported formats, oversized files, encrypted PDFs and documents with no readable text. It limits resumes to 60,000 characters and PDFs to 30 pages.

A scanned PDF is an image of text. The current parser cannot read its words. The user must run OCR elsewhere or paste the text.

## 6. Text normalization

Normalization makes different text forms easier to match. The app converts text to a consistent Unicode form, makes it lowercase and combines repeated whitespace.

For example, `PYTHON` and `python` should refer to the same skill. The app keeps punctuation important for names such as C++ and C#.

## 7. Skill extraction

`data/skills.json` contains canonical names and aliases. A canonical name is the standard label displayed to the user. An alias is another spelling of that skill.

Example: `scikit-learn`, `sklearn` and `scikit learn` all map to **scikit-learn**.

The app searches for these terms with boundaries. That prevents Java from matching inside JavaScript, and SQL from matching inside MySQL. It records the first line containing each skill as evidence.

The app classifies English context before comparing skill sets. Positive mentions can count as evidence; learning goals and explicit negative statements do not. Conflicting positive and negative statements are flagged for review. A phrase such as Machine Learning is treated as a skill name rather than a learning-status cue.

The app then compares two sets:

- Matching skills: present in both documents.
- Skills to review: active job skills without positive resume evidence, including learning, negative and conflicting mentions.
- Other resume skills: present in the resume but not detected in the job description.

This is dictionary-based NLP. It does not discover every possible skill automatically. If a job asks for SAP and it is not in the catalog, add SAP to the custom-skills box.

## 8. What is an embedding?

An embedding is a list of numbers representing text. A pretrained model produces these numbers so text with related meanings often has similar representations.

For example, “analyzing datasets” and “working with data to find patterns” may be related even though they use different words. Semantic comparison can capture some of this relationship.

The project uses `all-MiniLM-L6-v2`, a pretrained Sentence Transformers model. We use the existing model; we did not train it from scratch or fine-tune it on resumes.

## 9. Why split the documents?

Embedding models accept a limited number of tokens at a time. Tokens are pieces of words or text understood by the model. Sending a long resume directly could cause later text to be cut off.

The app uses the model tokenizer to split documents into shorter chunks. It embeds each chunk and takes a weighted average. Longer chunks receive proportionally more weight.

This lets the application consider text throughout the document. A limitation is that averaging can hide differences between individual sections or job requirements.

## 10. Cosine similarity

Cosine similarity compares the direction of two numerical vectors. Here the vectors represent the resume and the job description.

A higher value means the representations are more similar. The app displays a number from 0 to 100 by clipping negative values to zero and multiplying by 100.

It is a text-comparison score. It has not been tested as a hiring prediction. Do not describe it as a guaranteed ATS score.

## 11. The keyword engine

The keyword mode works without a downloaded AI model. It uses **TF-IDF**:

- TF: how often a term appears in a document.
- IDF: how distinctive the term is across the compared documents.

This mode represents words and pairs of words as numerical vectors, then applies cosine similarity. It compares wording. It cannot understand synonyms as well as a semantic model.

Both modes are useful for demonstration. The interface clearly labels the selected mode. If the AI model fails to load, the app shows an error instead of pretending keyword results came from AI.

## 12. Improvement suggestions and learning plans

The current suggestions are rules written in Python. Job skills are classified as required, preferred or unspecified from explicit wording and headings. Overall skill coverage remains unweighted; separate category scores show coverage in each group. Explicitly excluded job skills are shown for review and omitted from coverage. These rules can make mistakes.

Practice plans put required skills first, followed by unspecified and preferred skills. Selected skills have a concrete exercise, validation checks and a curated learning link. Others receive a clearly labeled fallback exercise. The plan adapts its opening instruction for learning and conflicting mentions. These are curated templates, not personalized courses or LLM-generated responses.

The Action plan tab also builds a daily study routine. Choose 7, 14 or 30 days and a daily budget of 30, 60, 90 or 120 minutes. Common skills have four starter topics, a mini-project and a review; other skills have a generic starter template. Each 30-minute session splits time between learning, practice and review. Video and reading links help you study; search links are labeled as unreviewed. These topics are an introduction, not every topic in a subject.

If the tasks need more days than selected, the planner extends the schedule so no gap is left out. Longer plans include reinforcement. You can mark days complete and export the schedule. Completion is a self-reported session value and does not change match scores or verify proficiency. Changing study preferences does not rerun the embedding model.

Never add a skill just to raise the score. Add it only if you can demonstrate it.

## 13. How the interface works

`app.py` creates two input columns. Both the resume and job description accept typed/pasted text or PDF, DOCX and TXT uploads. The sidebar lets users select an engine and add custom skills. The Analyze button is disabled after a successful analysis until an input or setting changes; invalid uploads block analysis.

When Analyze is clicked, the app validates inputs, calls `analyze()` and stores the result in Streamlit session state. Session state keeps the current result across interface updates.

The app also stores the inputs used for that result. If the user edits the resume, job description, engine or custom skills, the old result is hidden until another analysis runs. This prevents the user from mistaking an old report for a new one.

The sample button loads fictional content. It does not import or claim information about you.

## 14. Reports and privacy

Before analyzing, the Mandatory JD requirements section lets you set a minimum experience value, accepted qualifications and an optional pass-out-year range. Its button suggests values from common JD wording; check and correct those values yourself. The resume must state all three details for the checks to pass. A missing work-experience statement is different from an explicit zero-year fresher statement.

The new `analyzer/requirements.py` module reads explicit experience totals or month/year work dates, avoids double-counting overlapping work periods, recognizes common qualification aliases and associates pass-out years with education entries. Internships count only when selected. Incomplete degrees, conflicting totals, year-only work dates and future dates need review. Results and their supporting text are exported with the report. These are checks of document statements; they do not verify credentials or make a final job-eligibility decision.

The PDF report is a paginated document, Markdown is readable text, and JSON is structured data another program can use. All contain excerpts from the input documents as evidence. PDF generation uses ReportLab in memory. Its bundled font replaces unsupported characters with `?`; JSON and Markdown preserve the original text.

The app does not write uploads to disk or call an LLM API. It holds inputs and results in server memory during the active session. If you run it on your laptop, the processing runs there. If you host it online, uploads reach that hosting server.

The model download is separate from resume processing. Model weights are cached, but your documents are not used to train the model.

## 15. Tests and what they prove

The test suite checks the sample skill denominator, punctuation-aware aliases, custom skills, Unicode, invalid input, no detected skills, parser errors, DOCX tables, PDF extraction, model chunking and user interactions.

The Streamlit tests load samples, analyze, verify metrics and exports, change inputs to check stale-report handling, and clear the session. A deterministic model double tests semantic integration without a network download.

Passing these tests shows that the checked behavior works. It does not establish recruitment accuracy. See VALIDATION.md for the exact build checks and any real-model limitation.

## 16. How to demonstrate it to a senior

1. Explain the problem: people need to see whether their resume clearly mentions skills requested for a role.
2. Open the app and load the sample.
3. Run Keyword analysis and explain the two separate scores.
4. Show evidence for a matching and a missing skill.
5. Add a custom skill and analyze again.
6. Run AI mode after installing the model dependencies.
7. Download a report.
8. State the limits: dictionary coverage, negation, equal weighting and no hiring prediction.

## 17. Interview explanation

“I built an AI Job Match and Skill Gap Analyzer using Python and Streamlit. It accepts a resume and job description. I integrated a pretrained Sentence Transformers model to compare their text meaning using embeddings and cosine similarity. I also implemented a TF-IDF keyword mode. A separate skill-matching module identifies skills mentioned in both documents and job skills not found in the resume. The app displays the supporting text and exports reports. I added file validation and automated tests. The score is an estimated document similarity, not a hiring prediction.”

Use “I built” only after you have studied, run and can explain the code yourself. Be clear that the embedding model is pretrained.

## 18. Common interview questions

**Is this generative AI or traditional ML?**

It uses a pretrained deep-learning NLP embedding model for semantic similarity. It does not generate text using an LLM. Keyword similarity uses TF-IDF, and skill matching and suggestions are rule-based.

**Why Sentence Transformers?**

It produces sentence or text embeddings suitable for semantic comparison. It can capture related meaning even when wording differs.

**Why Streamlit?**

It lets me build an interactive Python interface quickly and focus on the NLP workflow.

**Did you train a model?**

No. I integrated a pretrained model. Training or fine-tuning on labeled resume-job pairs would be a future extension.

**Why not use only keyword matching?**

Keyword matching explains exact skill mentions well. Semantic embeddings help compare broader meaning. I show both approaches separately because they measure different things.

**What happens when a resume is long?**

The semantic engine splits the text with the model tokenizer, embeds the chunks and computes a weighted average.

**What are the main challenges?**

Extracting clean text, handling aliases, preventing partial-word matches, avoiding document truncation, reporting model failures clearly and explaining the limits of a match score.

**How would you evaluate it?**

First, create consented or synthetic resume-job examples with human-labeled skill mentions and compare extraction precision and recall. Then compare similarity rankings with human judgments across roles. Separate those evaluations from hiring-outcome prediction. Do not invent an accuracy percentage.

**What would you improve next?**

More robust context parsing, section-aware semantic comparisons, broader curated learning resources, OCR and a human-labeled evaluation set. Basic English negation rules and required/preferred classification are already included.

## 19. Resume bullet after you understand and run it

Built a Python and Streamlit resume–job comparison application using pretrained Sentence Transformer embeddings, TF-IDF and cosine similarity; added skill evidence, gap analysis, report exports and automated tests.

Do not add made-up accuracy, user counts or time savings. Use only measurements you actually collect.
