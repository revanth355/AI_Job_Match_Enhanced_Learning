# Accuracy evaluation

Run `python evaluate.py` from the project folder. The committed cases cover multiple roles, alias boundaries, negation, priority wording, relevant experience and degree subjects. Expected labels are written independently of analyzer output. The JSON result includes micro precision/recall/F1 for matched and required skills, exact-case counts, requirement-check counts and every disagreement. No case is silently dropped.

These are **synthetic development examples labeled by the assistant**, not independently human-reviewed resumes. Do not advertise these results as real-world accuracy. The benchmark evaluates text-level rules, not PDF/DOCX layout extraction, semantic similarity quality, candidate proficiency or hiring outcomes. Do not keep tuning against this small set and call it a held-out test.

## Human review protocol

1. Collect consented, anonymized examples across roles, experience levels and document layouts. Keep personal documents outside the public repository.
2. Have a reviewer label `matched`, `required` and optional `checks` from the two texts before looking at predictions. A matched skill needs positive resume evidence, not a course goal or negated mention. Distinguish missing evidence from absence of ability.
3. Use a second reviewer for ambiguous cases and record the adjudication in `notes`. Record `reviewer`, `review_date` and `human_reviewed: true` only after that work actually happens.
4. Keep a separate held-out file that is never used to tune rules. Run `python evaluate.py --cases path/to/held_out.json --output path/to/results.json`.
5. Report sample size, role distribution, label protocol, disagreements and false positives/negatives alongside metrics. Add extraction-layout cases separately. Use more independent data before making reliability claims.

For each failure, inspect `latest_results.json` and the original case; change labels only when the independent evidence supports that correction, not just to match the implementation.
