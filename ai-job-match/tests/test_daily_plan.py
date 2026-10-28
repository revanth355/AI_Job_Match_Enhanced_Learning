import unittest
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from unittest.mock import patch

from pypdf import PdfReader
from streamlit.testing.v1 import AppTest
from analyzer.core import analyze, markdown_report
from analyzer.plans import build_daily_plan, learning_step, study_resources
from analyzer.reports import pdf_report

ROOT = Path(__file__).resolve().parents[1]


class DailyPlanTests(unittest.TestCase):
    def test_every_gap_and_topic_fits_budget_with_extension(self):
        skills = [learning_step(s, 'required', 'not found') for s in ['Excel', 'SQL', 'Python', 'Git', 'Pandas']]
        plan = build_daily_plan(skills, 7, 30)
        self.assertTrue(plan['extended'])
        self.assertEqual(plan['total_days'], 30)
        self.assertEqual(plan['starter_sessions'], 30)
        self.assertEqual(set(plan['skills']), {'Excel', 'SQL', 'Python', 'Git', 'Pandas'})
        self.assertTrue(all(d['minutes'] <= 30 for d in plan['days']))
        sessions = [s for d in plan['days'] for s in d['sessions']]
        for skill in plan['skills']:
            self.assertEqual(len([s for s in sessions if s['skill'] == skill]), 6)
        self.assertTrue(all(s['learn_minutes'] + s['practice_minutes'] + s['review_minutes'] == s['minutes'] for s in sessions))

    def test_priority_order_and_longer_plan_reinforcement(self):
        steps = [learning_step('Git', 'preferred', 'not found'), learning_step('SQL', 'required', 'learning')]
        plan = build_daily_plan(steps, 30, 120)
        sessions = [s for d in plan['days'] for s in d['sessions']]
        self.assertEqual(sessions[0]['skill'], 'SQL')
        self.assertEqual(sessions[0]['resume_status'], 'learning')
        self.assertFalse(plan['extended'])
        self.assertEqual(len(plan['days']), 30)
        self.assertTrue(any(s['topic'].startswith('Reinforcement:') for s in sessions))
        self.assertTrue(all(0 < d['minutes'] <= 120 for d in plan['days']))

    def test_empty_and_invalid_settings(self):
        self.assertEqual(build_daily_plan([])['days'], [])
        self.assertEqual(build_daily_plan([])['total_days'], 0)
        for days, minutes in [(1, 60), (7, 15), (14, 999)]:
            with self.assertRaises(ValueError):
                build_daily_plan([], days, minutes)

    def test_unknown_skill_has_labeled_curriculum_and_encoded_searches(self):
        skill = 'Example C++ & Tools'
        plan = build_daily_plan([learning_step(skill, 'required', 'not found')], 7, 60)
        task = plan['days'][0]['sessions'][0]
        self.assertEqual(task['curriculum'], 'generic starter template')
        self.assertTrue(all(not r['curated'] for r in task['resources']))
        video = next(r for r in task['resources'] if r['kind'] == 'video search')
        self.assertIn(skill, parse_qs(urlparse(video['url']).query)['search_query'][0])
        self.assertTrue(all(urlparse(r['url']).scheme == 'https' for r in task['resources']))

    def test_sample_has_real_video_links_and_exports_full_plan(self):
        result = analyze((ROOT / 'samples/resume.txt').read_text(), (ROOT / 'samples/job_description.txt').read_text())
        self.assertEqual(result['daily_plan']['total_days'], 15)
        self.assertEqual(set(result['daily_plan']['skills']), set(result['skills_not_found']))
        for skill in result['skills_not_found']:
            self.assertTrue(any(r['kind'] == 'video' and r['curated'] for r in study_resources(skill, 'fundamentals')))
        md = markdown_report(result)
        self.assertIn('## Daily study plan', md)
        self.assertIn('### Day 15', md)
        reader = PdfReader(BytesIO(pdf_report(result)))
        text = '\n'.join(p.extract_text() for p in reader.pages)
        self.assertIn('Day 15', text)
        self.assertIn('Video and reading links', text)
        uris = [str(a.get_object()['/A'].get('/URI', '')) for p in reader.pages
                for a in p.get('/Annots', []) if '/A' in a.get_object()]
        self.assertIn('https://www.youtube.com/watch?v=LgXzzu68j7M', uris)


class DailyPlanAppTests(unittest.TestCase):
    def test_settings_and_progress_update_exports_without_reanalysis(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        old_pdf = app.session_state['pdf_report']
        with patch('analyzer.core.analyze', side_effect=RuntimeError('Must not reanalyze')):
            app.selectbox(key='plan_days').set_value(7).run(timeout=30)
            app.selectbox(key='plan_minutes').set_value(30).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[1].value, '44.4%')
            self.assertTrue(any('30 days' in i.value for i in app.info))
            self.assertNotEqual(old_pdf, app.session_state['pdf_report'])
            next(c for c in app.checkbox if c.label == "I finished today's practice and self-check").check().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['pdf_signature'][-1], (1,))
            day_picker = next(s for s in app.selectbox if s.label == 'Choose study day')
            day_picker.set_value(2).run(timeout=30)
            self.assertFalse(next(c for c in app.checkbox if c.label == "I finished today's practice and self-check").value)
            next(s for s in app.selectbox if s.label == 'Choose study day').set_value(1).run(timeout=30)
            self.assertTrue(next(c for c in app.checkbox if c.label == "I finished today's practice and self-check").value)


if __name__ == '__main__':
    unittest.main()
