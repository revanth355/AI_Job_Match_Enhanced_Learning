"""Curated practice tasks and a time-budgeted starter study planner."""
from math import ceil
from urllib.parse import urlencode
from .lessons import LEVELS, lesson

RESOURCES = {
    "Python": ("Python tutorial", "https://docs.python.org/3/tutorial/", "Build a CSV summary script with functions and error handling.", "Check normal, empty and malformed inputs with three tests."),
    "SQL": ("PostgreSQL SQL tutorial", "https://www.postgresql.org/docs/current/tutorial.html", "Create customers and orders tables; write JOIN, GROUP BY and filtering queries.", "Check query totals against a small dataset with known answers."),
    "Pandas": ("pandas getting started", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "Clean a small CSV, handle missing values and summarize results by category.", "Assert row counts, missing-value handling and expected summary totals."),
    "Excel": ("Microsoft Excel help and learning", "https://support.microsoft.com/en-us/excel/", "Create a budget workbook with formulas, a pivot table and a chart.", "Reconcile totals manually and test blank cells and new rows."),
    "Power BI": ("Microsoft Learn for Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi", "Import a sample sales dataset and create a dashboard with measures and filters.", "Compare dashboard totals with the source data and test each filter."),
    "Git": ("Pro Git book", "https://git-scm.com/book/en/v2", "Create a repository, make a feature branch, merge it and resolve a practice conflict.", "Show a readable commit history and explain how you reverted a change."),
    "Data Visualization": ("Matplotlib tutorials", "https://matplotlib.org/stable/tutorials/index.html", "Create a bar chart and a trend chart with clear units, labels and a written takeaway.", "Check plotted values against the dataset and explain why each chart fits the question."),
    "Statistics": ("NIST statistical methods handbook", "https://www.itl.nist.gov/div898/handbook/", "Use a small dataset to calculate mean, median, spread and a confidence interval; explain the assumptions.", "Check calculations on a hand-worked example and describe uncertainty without claiming causation."),
    "Communication": ("British Council speaking practice tips", "https://learnenglish.britishcouncil.org/level/improve-your-english-level/how-improve-your-english-speaking", "Present one project in three minutes: problem, method, result and limitation.", "Ask a peer to summarize your conclusion and revise anything unclear."),
    "Teamwork": (None, None, "Work with a peer on a small feature using a written task split and a review.", "Document your contribution, feedback received and how you resolved a disagreement."),
}

# These are starter curricula, not exhaustive syllabuses or mastery estimates.
TOPICS = {
    "Python": [("Variables and data types", "Store and print five values of different types."), ("Conditions and loops", "Filter a list and summarize its values using a loop."), ("Functions and collections", "Write a function that summarizes a list of dictionaries."), ("Files and exceptions", "Read a small CSV and handle a missing file clearly.")],
    "SQL": [("Tables, keys and SELECT", "Create one table and retrieve a few columns."), ("Filtering and sorting", "Write five WHERE and ORDER BY queries."), ("JOINs", "Join customers and orders and check the row count."), ("Aggregates and GROUP BY", "Calculate totals by customer and filter groups with HAVING.")],
    "Pandas": [("DataFrames and CSV input", "Load a CSV and inspect shape, types and the first rows."), ("Selection and missing values", "Filter records and explain your missing-value treatment."), ("Grouping and merging", "Combine two small tables and summarize by category."), ("Export and reproducibility", "Save a cleaned CSV and reproduce its summary from a fresh run.")],
    "Excel": [("Cells, tables and data types", "Create a 15-row expense table with clear column headings."), ("Formulas and references", "Use SUM, AVERAGE and IF; test relative and absolute references."), ("Sorting, filtering and cleaning", "Filter the table and correct blanks and inconsistent labels."), ("Pivot tables and charts", "Create a category summary and a chart with clear units.")],
    "Power BI": [("Import data and Power Query", "Import a sample CSV and correct types and missing values."), ("Relationships and data model", "Relate two small tables and explain the join keys."), ("Measures and basic DAX", "Create a total-sales measure and check it against the source."), ("Visuals, slicers and interactions", "Build a report page and test how its filters affect every visual.")],
    "Git": [("Repository and commits", "Initialize a repository and make two descriptive commits."), ("Branches and merges", "Create a branch, edit a file and merge the change."), ("Conflicts and recovery", "Resolve a practice conflict and revert one safe test commit."), ("Remote collaboration", "Push to a practice repository and review a small change with a peer.")],
    "Data Visualization": [("Choose an appropriate chart", "Match three questions to bar, line or scatter charts."), ("Labels, units and axes", "Plot a small dataset with a title, labels and readable scales."), ("Comparison and trends", "Create a bar and line chart and write one supported takeaway for each."), ("Accessible and honest presentation", "Remove clutter and check color contrast, units and misleading scales.")],
    "Statistics": [("Mean, median and spread", "Calculate summary statistics on ten values and check them by hand."), ("Distributions and sampling", "Plot a small distribution and explain sample versus population."), ("Correlation and uncertainty", "Compare two variables and explain why correlation does not establish causation."), ("Confidence intervals and hypotheses", "Explain a confidence interval and a null hypothesis using a simple worked example.")],
    "Communication": [("Audience and main message", "Write one clear takeaway about a project for a nontechnical audience."), ("Structure and concise writing", "Write a five-sentence problem-method-result-limitation summary."), ("Speaking and active listening", "Record a two-minute explanation and summarize a peer's feedback."), ("Questions and feedback", "Answer three likely project questions and revise an unclear explanation.")],
    "Teamwork": [("Roles and shared goals", "Agree a small task and write who owns each part."), ("Progress updates", "Write a concise update with progress, next step and one blocker."), ("Review and disagreement", "Review a peer's change and propose a respectful resolution to one disagreement."), ("Retrospective", "Document what worked and one change to try in the next task.")],
}

VIDEOS = {
    "Python": ("Microsoft Python for Beginners video series", "https://learn.microsoft.com/en-us/shows/intro-to-python-development/"),
    "SQL": ("Microsoft T-SQL for Beginners video series (SQL Server dialect)", "https://learn.microsoft.com/en-us/shows/programming-databases-with-t-sql-for-beginners/"),
    "Pandas": ("pandas community video tutorials", "https://pandas.pydata.org/docs/getting_started/tutorials.html#video-tutorials"),
    "Excel": ("Excel Tutorial for Beginners - Kevin Stratvert", "https://www.youtube.com/watch?v=LgXzzu68j7M"),
    "Power BI": ("Power BI Tutorial for Beginners", "https://www.youtube.com/watch?v=VaOhNqNtGGE"),
    "Git": ("Git introductory videos", "https://git-scm.com/videos"),
    "Data Visualization": ("Matplotlib Introduction - codebasics playlist", "https://www.youtube.com/playlist?list=PLeo1K3hjS3uu4Lr8_kro2AqaO6CFYgKOl"),
    "Statistics": ("StatQuest statistics videos", "https://statquest.org/video_index.html#statistics"),
    "Communication": ("Julian Treasure: How to speak so that people want to listen - TED", "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"),
}


def study_resources(skill, topic, level='Beginner'):
    """Fallbacks are clearly marked searches; no links contain document excerpts."""
    reading = RESOURCES.get(skill)
    links = []
    if skill in VIDEOS:
        title, url = VIDEOS[skill]
        links.append({"kind": "video", "title": title, "url": url, "curated": True})
    links.append({"kind": "video search", "title": f"Search YouTube: {skill} / {topic}",
                  "url": "https://www.youtube.com/results?" + urlencode({"search_query": f"{skill} {topic} {level.lower()} tutorial"}), "curated": False})
    if reading and reading[1]:
        links.append({"kind": "reading", "title": reading[0], "url": reading[1], "curated": True})
    elif skill == "Statistics":
        links.append({"kind": "reading", "title": "NIST statistical methods handbook", "url": "https://www.itl.nist.gov/div898/handbook/", "curated": True})
    else:
        links.append({"kind": "reading search", "title": f"Find beginner reading for {skill}",
                      "url": "https://www.google.com/search?" + urlencode({"q": f"{skill} beginner documentation {topic}"}), "curated": False})
    return links


def build_daily_plan(learning_plan, requested_days=14, minutes_per_day=60, levels=None):
    """Schedule every starter topic; extend the horizon instead of dropping gaps."""
    if requested_days not in (7, 14, 30) or minutes_per_day not in (30, 60, 90, 120):
        raise ValueError("Choose 7, 14 or 30 days and 30, 60, 90 or 120 minutes per day.")
    levels = levels or {}
    skills = {s['skill'] for s in learning_plan}
    if not isinstance(levels, dict) or any(s not in skills or level not in LEVELS for s, level in levels.items()):
        raise ValueError('Choose a valid level for each skill in this plan.')
    levels = {s: levels.get(s, 'Beginner') for s in sorted(skills)}
    tasks, covered = [], set()
    ordered = sorted(learning_plan, key=lambda s: ({"required": 0, "unspecified": 1, "preferred": 2}[s["priority"]], s["skill"].casefold()))
    for step in ordered:
        skill = step["skill"]
        if skill in covered:
            continue
        covered.add(skill)
        topics = TOPICS.get(skill, [
            ("Choose a beginner syllabus", f"Find a trusted introduction to {skill} and list four topics relevant to the JD."),
            ("Understand the fundamentals", f"Explain three basic {skill} concepts from your chosen syllabus."),
            ("Follow a worked example", f"Reproduce one beginner {skill} example and explain each step."),
            ("Apply it independently", f"Adapt that {skill} example to a small task from this role.")])
        outline = list(topics) + [("Mini-project", step["practice"]), ("Review and self-check", step["check"])]
        level = levels[skill]
        # Beginners cover all foundations; experienced learners keep every skill
        # but use a shorter, more demanding practice path.
        selected = range(6) if level == 'Beginner' else range(2, 6) if level == 'Intermediate' else range(4, 6)
        for index in selected:
            topic, practice = outline[index]
            tasks.append({"skill": skill, "priority": step["priority"], "topic": topic,
                          'level': level, **lesson(skill, index, topic, practice, level),
                          "curriculum": "curated starter topics" if skill in TOPICS else "generic starter template",
                          "resume_status": step["resume_status"], "goal": step["goal"],
                          "practice": practice, "check": "Save your result and explain the steps without copying. Repeat the exercise if you cannot explain it.",
                          "minutes": 30, "learn_minutes": 10, "practice_minutes": 15, "review_minutes": 5,
                          "resources": study_resources(skill, topic, level)})
    slots = minutes_per_day // 30
    minimum_days = ceil(len(tasks) / slots)
    total_days = max(requested_days, minimum_days) if tasks else 0
    days, cursor = [], 0
    for day in range(1, total_days + 1):
        remaining_days = total_days - day + 1
        take = min(slots, ceil((len(tasks) - cursor) / remaining_days))
        sessions = tasks[cursor:cursor + take]
        cursor += take
        # Extra available days reinforce completed topics, rather than inventing
        # new skill requirements or claiming an exhaustive curriculum.
        if not sessions:
            previous = tasks[(day - 1) % len(tasks)]
            sessions = [{**previous, "topic": "Reinforcement: " + previous["topic"],
                         "practice": "Repeat or extend your earlier exercise without notes. " + previous["practice"]}]
        days.append({"day": day, "minutes": sum(s["minutes"] for s in sessions), "sessions": sessions})
    return {"requested_days": requested_days, "minutes_per_day": minutes_per_day,
            "total_days": total_days, "minimum_study_days": minimum_days,
            "extended": total_days > requested_days, "skills": list(dict.fromkeys(s["skill"] for s in ordered)),
            "starter_sessions": len(tasks), "completed_days": [], "days": days, 'levels': levels,
            "note": "A starter roadmap, not a complete syllabus or a promise of job readiness. Beginner covers foundations; Intermediate skips the first two introductory topics; Advanced focuses on a project and review. Check prerequisites before skipping topics. Each session budgets 10 minutes learning, 15 practice and 5 review. Save a progress backup and restore it in a later session to continue. Quizzes are formative practice, not verified proficiency; completing a plan does not change match scores. Search links are unreviewed results."}


def learning_step(skill, priority, status):
    entry = RESOURCES.get(skill)
    title, url, practice, check = entry if entry else (None, None,
        f"Choose a beginner exercise in {skill} relevant to this role and build one small working example.",
        "Write acceptance criteria before building; record the result and one limitation.")
    return {"skill": skill, "priority": priority, "resume_status": status,
            "goal": "Strengthen your existing learning with a demonstrable example." if status == "learning" else
                    "Review conflicting resume evidence before deciding whether to study or edit." if status == "review" else
                    "Check whether you already have truthful evidence; otherwise start with a small exercise.",
            "practice": practice, "check": check,
            "proof": "Save the exercise, checks and a short explanation in your portfolio. Add a resume claim only after you can demonstrate it.",
            "resource_title": title, "resource_url": url,
            "resource_note": "Curated learning resource." if url else "No curated link is available for this skill. Choose a trusted beginner resource before starting."}
