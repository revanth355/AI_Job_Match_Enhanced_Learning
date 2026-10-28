"""Reproducible offline benchmark. Labels are never generated from predictions."""
import argparse
from datetime import date
import json
from pathlib import Path
from analyzer.core import analyze
from analyzer.requirements import make_requirements


def evaluate(cases):
    if not cases or len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Provide cases with unique IDs.')
    totals = {name: {'tp': 0, 'fp': 0, 'fn': 0} for name in ('matched', 'required')}
    details, checks_correct, checks_total = [], 0, 0
    for case in cases:
        result = analyze(case['resume'], case['job'], custom=case.get('custom', []),
                         requirements=make_requirements(**case.get('settings', {})))
        errors = []
        for name, predicted in [('matched', result['matched_skills']), ('required', result['job_skills_by_priority']['required'])]:
            expected, actual = set(case[name]), set(predicted)
            for key, value in [('tp', len(expected & actual)), ('fp', len(actual - expected)), ('fn', len(expected - actual))]:
                totals[name][key] += value
            if expected != actual:
                errors.append({'field': name, 'false_positive': sorted(actual - expected), 'false_negative': sorted(expected - actual)})
        actual_checks = {c['requirement']: c['status'] for c in result['requirement_review']['checks']}
        for name, expected in case.get('checks', {}).items():
            checks_total += 1
            checks_correct += actual_checks.get(name) == expected
            if actual_checks.get(name) != expected:
                errors.append({'field': name, 'expected': expected, 'actual': actual_checks.get(name)})
        details.append({'id': case['id'], 'role': case['role'], 'errors': errors})
    for scores in totals.values():
        tp, fp, fn = scores['tp'], scores['fp'], scores['fn']
        scores['precision'] = round(tp / (tp + fp), 4) if tp + fp else None
        scores['recall'] = round(tp / (tp + fn), 4) if tp + fn else None
        scores['f1'] = round(2 * tp / (2 * tp + fp + fn), 4) if 2 * tp + fp + fn else None
    return {'date': str(date.today()), 'cases': len(cases),
            'human_reviewed_cases': sum(c.get('human_reviewed') is True and bool(c.get('reviewer')) for c in cases),
            'scope': 'Synthetic development benchmark authored and labeled by the assistant; not an independent real-world accuracy estimate. Human review and held-out real documents are still needed.',
            'metrics': totals, 'requirement_checks': {'correct': checks_correct, 'total': checks_total},
            'exact_cases': sum(not c['errors'] for c in details), 'details': details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', default='evaluation/cases.json')
    parser.add_argument('--output', default='evaluation/latest_results.json')
    args = parser.parse_args()
    report = evaluate(json.loads(Path(args.cases).read_text(encoding='utf-8')))
    Path(args.output).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'details'}, indent=2))


if __name__ == '__main__':
    main()
