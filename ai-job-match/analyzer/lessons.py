"""Authored short lessons and formative quizzes; not a proficiency certification."""
LEVELS = ('Beginner', 'Intermediate', 'Advanced')
PREREQUISITES = {'Pandas': 'Python functions, lists and dictionaries', 'Power BI': 'Tabular data, column types and basic aggregation',
                 'Data Visualization': 'Basic tables, categories and numeric data', 'Statistics': 'Arithmetic, percentages and basic algebra',
                 'SQL': 'Rows, columns and basic table relationships', 'Git': 'Basic files and terminal navigation'}

# Four topic-aligned lessons, in the same order as plans.TOPICS.
LESSONS = {
 'Python': [
  'A variable refers to a value. Numbers support arithmetic; strings hold text. Convert input explicitly and inspect its type before calculating.',
  'An if statement selects a branch. A for loop visits each item. Test empty collections and boundary values so your loop handles more than the example.',
  'A function groups reusable behavior and returns a result. Lists preserve sequences; dictionaries map keys to values. Avoid silently changing caller-owned data.',
  'Use a context manager to close files. Catch specific exceptions you can handle; report useful errors without hiding unexpected failures.'],
 'SQL': [
  'Each table has rows and columns. A primary key identifies a row. SELECT chooses columns; avoid assuming a query has a predictable order without ORDER BY.',
  'WHERE filters rows before grouping; ORDER BY sorts the result. NULL means unknown or absent, so test it with IS NULL instead of = NULL.',
  'INNER JOIN returns matching pairs. LEFT JOIN also keeps unmatched left rows. Duplicate keys can multiply rows; inspect counts before summing money.',
  'GROUP BY forms groups for aggregates such as SUM and COUNT. HAVING filters grouped results. COUNT(column) excludes NULL values; COUNT(*) counts rows.'],
 'Git': [
  'The working tree contains edits, the index stages a snapshot, and a commit records that snapshot. Inspect git diff before staging and committing.',
  'A branch is a movable reference to a commit. A merge combines histories. Use a small practice repository to understand the resulting graph.',
  'A conflict requires choosing the intended combined content. A revert records a new commit that undoes a previous change; test the result afterward.',
  'Fetch downloads remote history without integrating it into your branch. Review changes and communicate before combining work with a teammate.'],
 'Excel': [
  'Keep one observation per row and one field per column. Store numbers as numbers and dates consistently; merged cells make analysis harder.',
  'Relative references move when a formula is copied. Dollar signs lock a row or column, so $A$1 stays fixed. Test copied formulas at the bottom of a table.',
  'Filtering hides rows; it does not delete them. Preserve a raw copy before cleaning, and record how blanks and duplicate entries were handled.',
  'A pivot table groups records and summarizes values. Confirm SUM versus COUNT, refresh after source changes, and label chart units.'],
 'Pandas': [
  'A DataFrame is a labeled table. Inspect shape, dtypes and sample rows after reading a CSV; inferred types may not match the data meaning.',
  'Use explicit row and column selection. Missing-value handling depends on the task: dropping, filling and leaving missing values make different assumptions.',
  'A merge combines rows using keys. Duplicate keys can multiply rows. Check key uniqueness and use merge validation before trusting grouped totals.',
  'Separate raw input from derived output. Record cleaning steps in code and rerun from a fresh process to check that hidden state is not required.'],
 'Power BI': [
  'Power Query records transformations. Set correct types and inspect errors before loading; a number formatted as text can break an aggregation.',
  'Relationships propagate filters between tables. Understand key uniqueness, cardinality and filter direction before comparing totals.',
  'A measure is evaluated in filter context. A calculated column is computed per row during refresh. Test a measure with and without slicers.',
  'A slicer changes filter context. Visual interactions may filter or highlight other visuals; test each interaction and include clear titles and units.'],
 'Data Visualization': [
  'Use bars for category comparisons, lines for ordered time trends and scatter plots for relationships between two numeric variables. Match the chart to the question.',
  'Label axes with units, identify the time period and explain transformed scales. A bar chart usually needs a zero baseline for honest length comparisons.',
  'Compare like-for-like periods and denominators. A visible pattern does not establish its cause; write a takeaway that the data actually supports.',
  'Use labels or shapes as well as color. Remove decorative clutter, make text readable and disclose missing data and important uncertainty.'],
 'Statistics': [
  'The mean uses every value; the median is the middle ordered value. Outliers affect the mean more strongly. Report spread as well as a center.',
  'A sample is a subset of a population. Sampling method affects representativeness; a large biased sample may still mislead.',
  'Correlation describes association, not causation. Confounders and reverse causality can explain a relationship; inspect uncertainty and data collection.',
  'A frequentist 95% confidence procedure covers the fixed population parameter in 95% of repeated samples under its assumptions. A p-value is not the probability that the null hypothesis is true.'],
 'Communication': [
  'Identify the audience, the decision they need to make and one main takeaway. Explain necessary terms in language suited to that audience.',
  'Organize a project explanation around problem, method, result and limitation. Put the main point first and remove claims unsupported by evidence.',
  'Listen without planning a rebuttal. Restate the other person’s meaning and check your understanding before responding.',
  'Answer the question directly, give evidence and state uncertainty. Use feedback to revise the explanation and confirm that the revision helped.'],
 'Teamwork': [
  'Agree the shared outcome, task owners and definition of done. Make dependencies visible so nobody assumes another person owns the same task.',
  'An update should state completed work, next steps and blockers. Name the decision or help needed so teammates can act.',
  'Review the work against agreed criteria. Describe a specific concern and propose an alternative; resolve disagreements using evidence and shared goals.',
  'A retrospective identifies what helped and what hindered the team. Choose one concrete improvement with an owner and a way to check it.'],
}

QUIZZES = {
 'Python': ('What should a reusable calculation function usually do with its result?', ['Return it to the caller', 'Always write it to a global variable', 'Hide every exception'], 0, 'Returning a value lets callers reuse and test the calculation.'),
 'SQL': ('Which filter applies to grouped results?', ['ORDER BY', 'HAVING', 'SELECT'], 1, 'HAVING filters groups; WHERE filters rows before grouping.'),
 'Git': ('Which command records an undo as a new commit?', ['git fetch', 'git status', 'git revert'], 2, 'Revert records a new commit and preserves existing history.'),
 'Excel': ('Which reference keeps both row and column fixed when copied?', ['A1', '$A$1', 'A$1'], 1, '$ before the column and row locks both parts.'),
 'Pandas': ('What can happen when both merge keys contain duplicates?', ['Rows may multiply', 'Duplicates are always deleted', 'Only column names change'], 0, 'Many-to-many matches can create multiple output rows for each key.'),
 'Power BI': ('What can change a measure result interactively?', ['Renaming the report file', 'Moving a title', 'Changing filter context with a slicer'], 2, 'Measures are evaluated under the current filter context.'),
 'Data Visualization': ('Which chart best shows a trend over ordered dates?', ['An unlabeled pie chart', 'A line chart', 'A decorative icon'], 1, 'A line chart connects observations in temporal order.'),
 'Statistics': ('Does a correlation alone establish causation?', ['No; confounding or reverse causality may explain it', 'Yes, if it is positive', 'Yes, if the chart looks clear'], 0, 'Association alone does not identify a causal mechanism.'),
 'Communication': ('How should you check that you understood a colleague?', ['Interrupt immediately', 'Assume their intent', 'Paraphrase and ask for confirmation'], 2, 'Paraphrasing makes misunderstandings visible.'),
 'Teamwork': ('What makes a blocker update actionable?', ['Naming the help or decision needed', 'Only saying work is hard', 'Hiding dependencies'], 0, 'Specific requests let teammates help resolve a blocker.'),
}


def lesson(skill, index, topic, practice, level):
    entries = LESSONS.get(skill, [])
    text = entries[index] if index < len(entries) else 'Apply the earlier concepts independently. Define expected results, test an edge case, and explain one limitation of your solution.'
    challenge = {'Beginner': 'Follow one example, then recreate it without copying.',
                 'Intermediate': 'Solve independently and add at least two edge-case checks.',
                 'Advanced': 'Compare two approaches, explain trade-offs and test a failure case.'}[level]
    quiz = QUIZZES.get(skill) if index >= 4 else None
    return {'lesson': text, 'challenge': challenge, 'prerequisite': PREREQUISITES.get(skill, 'Basic familiarity with the topic and a suitable practice tool'),
            'topic_question': f'Explain {topic.lower()} using your own {skill} example. What could go wrong?',
            'rubric': ['Explain the concept in your own words.', 'Show a working example for: ' + practice, 'Demonstrate an edge case and state a limitation.'],
            'quiz': {'question': quiz[0], 'options': quiz[1], 'answer': quiz[2], 'explanation': quiz[3]} if quiz else None}
