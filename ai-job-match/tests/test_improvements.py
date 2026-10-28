import json
from io import BytesIO
from pathlib import Path
import unittest
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest
from analyzer.requirements import make_requirements, check_requirements, relevant_experience
from analyzer.plans import build_daily_plan, learning_step
from analyzer.progress import export_progress, import_progress, plan_key
from analyzer.core import analyze, markdown_report, find_skills
from analyzer.reports import pdf_report
from evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]
RESUME = 'Python developer building business applications.\nWork experience: 5 years\nPython experience: 2 years\nEducation\nB.Tech in CSE, 2024'
JOB = 'Required skills: Python, SQL. We build reliable software for our customers.'


class ImprovementTests(unittest.TestCase):
    def checks(self, text=RESUME, **kwargs):
        cfg = make_requirements(2, 'B.Tech', relevant_skills='Python', subjects='Computer Science', **kwargs)
        return {r['requirement']: r['status'] for r in check_requirements(text, cfg)['checks']}

    def test_scoped_experience_does_not_conflict_with_total(self):
        checks = self.checks()
        self.assertEqual(checks['Work experience'], 'met')
        self.assertEqual(checks['Relevant experience: Python'], 'met')
        self.assertEqual(checks['Degree subject'], 'met')

    def test_total_alone_cannot_satisfy_relevant_experience(self):
        checks = self.checks(RESUME.replace('Python experience: 2 years', 'Skills: Python'))
        self.assertEqual(checks['Relevant experience: Python'], 'review')

    def test_short_scoped_experience(self):
        self.assertEqual(self.checks(RESUME.replace('Python experience: 2 years', 'Python experience: 6 months'))['Relevant experience: Python'], 'not_met')
        self.assertEqual(self.checks(RESUME.replace('Python experience: 2 years', 'Python experience: at least 1 year'))['Relevant experience: Python'], 'review')

    def test_ambiguous_and_internship_claims(self):
        for statement in ['Less than 2 years of Python experience', 'No 2 years of Python experience', 'Python experience: 2 years in academic projects', '1-3 years of Python experience', 'Python experience: 2 years\nPython experience: 4 years']:
            with self.subTest(statement=statement):
                self.assertEqual(relevant_experience(statement, 'Python')['status'], 'review')
        self.assertEqual(relevant_experience('Internship Python experience: 2 years', 'Python')['status'], 'review')
        self.assertEqual(relevant_experience('Internship Python experience: 2 years', 'Python', True)['status'], 'stated')

    def test_subject_missing_wrong_and_unrelated_degree(self):
        self.assertEqual(self.checks(RESUME.replace('in CSE', 'in Mechanical Engineering'))['Degree subject'], 'not_met')
        self.assertEqual(self.checks(RESUME.replace('in CSE', ''))['Degree subject'], 'review')
        text = RESUME.replace('in CSE', 'in Mechanical Engineering') + '\nM.Sc in Computer Science, 2025'
        self.assertEqual(self.checks(text)['Degree subject'], 'not_met')

    def test_subject_and_batch_must_belong_to_same_degree(self):
        text = RESUME.replace('2024', '2020') + '\nB.Tech in Mechanical Engineering, 2024'
        result = check_requirements(text, make_requirements(2, 'B.Tech', '2024', subjects='CS'))
        self.assertEqual(result['checks'][2]['status'], 'not_met')

    def test_level_changes_path_but_keeps_every_skill(self):
        steps = [learning_step(s, 'required', 'not found') for s in ('Python', 'SQL')]
        beginner = build_daily_plan(steps)
        advanced = build_daily_plan(steps, levels={'Python': 'Advanced', 'SQL': 'Intermediate'})
        self.assertEqual(beginner['starter_sessions'], 12)
        self.assertEqual(advanced['starter_sessions'], 6)
        self.assertEqual(set(beginner['skills']), set(advanced['skills']))
        self.assertNotEqual(plan_key(beginner), plan_key(advanced))
        self.assertTrue(all(s['lesson'] and s['rubric'] for d in advanced['days'] for s in d['sessions']))
        self.assertTrue(any(s['quiz'] for d in advanced['days'] for s in d['sessions']))
        with self.assertRaises(ValueError):
            build_daily_plan(steps, levels={'Python': 'Expert'})

    def test_backup_round_trip_and_no_document_text(self):
        result = analyze(RESUME, JOB)
        plan = result['daily_plan']
        plan['completed_days'] = [1, 3]
        raw = export_progress(plan)
        restored = import_progress(raw, result['learning_plan'])
        self.assertEqual(restored['completed_days'], [1, 3])
        self.assertEqual(plan_key(restored), plan_key(plan))
        self.assertNotIn(RESUME, raw)
        self.assertNotIn('evidence', raw)

    def test_backup_rejects_wrong_plan_and_bad_data(self):
        steps = [learning_step('SQL', 'required', 'not found')]
        data = json.loads(export_progress(build_daily_plan(steps)))
        for mutation in [{'version': 99}, {'completed_days': [999]}, {'completed_days': [True]}, {'completed_days': [[1]]}, {'levels': {'SQL': 'Expert'}}, {'plan_key': 'wrong'}]:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                import_progress(json.dumps({**data, **mutation}), steps)
        for raw in ['{', '[]', 'x' * 100001]:
            with self.assertRaises(ValueError):
                import_progress(raw, steps)

    def test_benchmark_metrics_report_disagreement_without_relabeling(self):
        cases = [{'id': 'one', 'role': 'Example', 'resume': RESUME, 'job': JOB,
                  'matched': ['Python', 'SQL'], 'required': ['Python', 'SQL'], 'human_reviewed': False}]
        report = evaluate(cases)
        self.assertEqual(report['metrics']['matched']['fn'], 1)
        self.assertEqual(report['metrics']['matched']['recall'], 0.5)
        self.assertEqual(report['human_reviewed_cases'], 0)
        self.assertTrue(report['details'][0]['errors'])

    def test_canonical_skill_names_are_recognized(self):
        self.assertIn('Testing', find_skills('Testing'))

    def test_personalized_exports_contain_lesson_and_quiz(self):
        result = analyze(RESUME, JOB)
        result['daily_plan'] = build_daily_plan(result['learning_plan'], 7, 120, {'SQL': 'Advanced'})
        self.assertIn('Quiz:', markdown_report(result))
        text = '\n'.join(p.extract_text() for p in PdfReader(BytesIO(pdf_report(result))).pages)
        self.assertIn('Level: Advanced', text)
        self.assertIn('Quiz:', text)


class ImprovementAppTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        app.text_area(key='resume_text').set_value(RESUME).run()
        app.text_area(key='job_text').set_value(JOB).run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        return app

    def test_cross_session_restore(self):
        steps = analyze(RESUME, JOB)['learning_plan']
        plan = build_daily_plan(steps, 7, 30, {'SQL': 'Advanced'})
        plan['completed_days'] = [1, 2]
        app = self.app()
        app.file_uploader(key='progress_backup').upload('progress.json', export_progress(plan).encode(), 'application/json').run()
        next(b for b in app.button if b.label == 'Restore progress').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key='plan_days').value, 7)
        self.assertEqual(app.selectbox(key='level_SQL').value, 'Advanced')
        self.assertEqual(app.session_state['pdf_signature'][-1], (1, 2))
        self.assertTrue(next(c for c in app.checkbox if c.label == "I finished today's practice and self-check").value)

    def test_invalid_backup_does_not_destroy_current_progress(self):
        app = self.app()
        next(c for c in app.checkbox if c.label == "I finished today's practice and self-check").check().run()
        app.file_uploader(key='progress_backup').upload('bad.json', b'{}', 'application/json').run()
        next(b for b in app.button if b.label == 'Restore progress').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state['pdf_signature'][-1], (1,))

    def test_level_change_updates_pdf_without_score_change(self):
        app = self.app()
        before = app.session_state['pdf_report']
        score = app.metric[1].value
        app.selectbox(key='level_SQL').set_value('Advanced').run(timeout=30)
        self.assertFalse(app.exception)
        self.assertNotEqual(before, app.session_state['pdf_report'])
        self.assertEqual(app.metric[1].value, score)

    def test_new_requirement_controls_and_stale_report(self):
        app = self.app()
        app.number_input(key='required_years').set_value(2).run()
        app.text_input(key='required_qualifications').set_value('B.Tech').run()
        app.text_input(key='relevant_skills').set_value('Python').run()
        app.text_input(key='degree_subjects').set_value('CS').run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['requirement_review']['summary'], 'Meets configured checks')
        app.text_input(key='degree_subjects').set_value('Mechanical Engineering').run()
        self.assertEqual(len(app.metric), 0)

    def test_quiz_feedback(self):
        app = self.app()
        app.selectbox(key='level_SQL').set_value('Advanced').run(timeout=30)
        quiz = next(r for r in app.radio if r.label == 'Which filter applies to grouped results?')
        quiz.set_value('HAVING').run()
        next(b for b in app.button if b.label == 'Check answer').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('Correct.' in item.value for item in app.success))
