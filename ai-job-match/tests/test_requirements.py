import unittest
from datetime import date
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest

from analyzer.requirements import make_requirements, check_requirements, experience_evidence, education_evidence, suggest_requirements
from analyzer.core import analyze, markdown_report
from analyzer.reports import pdf_report

TODAY = date(2026, 10, 26)
RESUME = "Python developer delivering reliable data products.\nWork experience: 3 years\nEducation\nB.Tech in Computer Science, 2024"
JOB = "Python developer with 2-4 years of experience.\nRequired qualification: B.Tech.\nGraduation batch: 2023-2025."
APP = str(Path(__file__).resolve().parents[1] / 'app.py')


class RequirementTests(unittest.TestCase):
    def cfg(self, minimum=2, qualification='B.Tech', years='2023-2025'):
        return make_requirements(minimum, qualification, years)

    def check(self, text, cfg=None):
        return check_requirements(text, cfg or self.cfg(), today=TODAY)

    def test_all_mandatory_checks_met(self):
        result = self.check(RESUME)
        self.assertEqual(result['summary'], 'Meets configured checks')
        self.assertEqual([r['status'] for r in result['checks']], ['met', 'met', 'met'])

    def test_missing_experience_is_not_zero(self):
        missing = self.check('Python developer building software.\nEducation\nB.Tech, 2024', self.cfg(0))
        self.assertEqual(missing['checks'][0]['status'], 'missing')
        self.assertEqual(missing['summary'], 'Needs review')
        zero = self.check('Fresher with Python projects.\nEducation\nB.Tech, 2024', self.cfg(0))
        self.assertEqual(zero['checks'][0]['status'], 'met')
        self.assertEqual(zero['experience']['minimum_years'], 0)

    def test_insufficient_experience_does_not_pass(self):
        result = self.check(RESUME.replace('3 years', '1 year'))
        self.assertEqual(result['checks'][0]['status'], 'not_met')
        self.assertEqual(result['summary'], 'Does not meet configured checks')

    def test_mismatched_qualification_does_not_pass(self):
        self.assertEqual(self.check(RESUME, self.cfg(qualification='MCA'))['checks'][1]['status'], 'not_met')
        self.assertEqual(self.check(RESUME, self.cfg(qualification="Bachelor's degree"))['checks'][1]['status'], 'met')

    def test_incomplete_or_future_degree_requires_review(self):
        for degree in ['Pursuing B.Tech, expected 2027', 'B.Tech, 2027', 'Did not complete B.Tech, 2024']:
            with self.subTest(degree=degree):
                result = self.check('Work experience: 3 years\nEducation\n' + degree)
                self.assertEqual(result['checks'][1]['status'], 'review')
                self.assertEqual(result['checks'][2]['status'], 'review')

    def test_graduation_year_is_mandatory_even_without_batch_filter(self):
        result = self.check(RESUME.replace(', 2024', ''), self.cfg(years=''))
        self.assertEqual(result['checks'][2]['status'], 'missing')
        self.assertEqual(result['summary'], 'Needs review')

    def test_wrong_batch_does_not_pass(self):
        self.assertEqual(self.check(RESUME, self.cfg(years='2025-2026'))['checks'][2]['status'], 'not_met')

    def test_birth_and_work_dates_do_not_fill_graduation_year(self):
        text = 'Work Experience\nDeveloper, Jan 2021 - Jan 2024\nEducation\nB.Tech\nDOB: 2001'
        result = self.check(text)
        self.assertEqual(result['checks'][0]['status'], 'met')
        self.assertEqual(result['checks'][2]['status'], 'missing')

    def test_graduation_belongs_to_accepted_degree(self):
        text = 'Work experience: 3 years\nEducation\nB.Tech, 2020\nMCA, 2024'
        self.assertEqual(self.check(text)['checks'][2]['status'], 'not_met')

    def test_overlap_counted_once_and_education_dates_ignored(self):
        text = 'Work Experience\nDeveloper\nJan 2020 - Jan 2022\nAnalyst\nJan 2021 - Jan 2023\nEducation\nB.Tech Jan 2016 - Jan 2020'
        result = experience_evidence(text, today=TODAY)
        self.assertEqual(result['minimum_years'], 3)
        self.assertEqual(result['status'], 'stated')

    def test_internships_are_explicitly_configurable(self):
        text = 'Work Experience\nIntern\nExample Company\nJan 2020 - Jan 2021\nDeveloper\nAnother Company\nJan 2021 - Jan 2023'
        self.assertEqual(experience_evidence(text, today=TODAY)['minimum_years'], 2)
        self.assertEqual(experience_evidence(text, include_internships=True, today=TODAY)['minimum_years'], 3)

    def test_present_dates_and_imprecise_dates(self):
        result = experience_evidence('Work Experience\nDeveloper\nOct 2024 - Present', today=TODAY)
        self.assertEqual(result['minimum_years'], 2)
        for dates in ['2020 - 2024', 'Jan 2027 - Jan 2028', 'Jan 2024 - Jan 2020']:
            self.assertEqual(experience_evidence('Work Experience\nDeveloper\n' + dates, today=TODAY)['status'], 'review')

    def test_experience_months_ranges_and_lower_bounds(self):
        for statement in ['2 years 6 months of experience', 'Work experience: 2 years 6 months', '30 months of experience']:
            self.assertEqual(experience_evidence(statement)['minimum_years'], 2.5)
        result = self.check(RESUME.replace('3 years', '2-4 years'), self.cfg(3))
        self.assertEqual(result['checks'][0]['status'], 'review')
        result = self.check(RESUME.replace('3 years', '2+ years'), self.cfg(3))
        self.assertEqual(result['checks'][0]['status'], 'review')

    def test_scoped_negation_or_conflicting_totals_do_not_pass(self):
        self.assertIsNone(experience_evidence('No experience with Python.')['minimum_years'])
        self.assertIsNone(experience_evidence('No prior experience with Python.')['minimum_years'])
        self.assertEqual(experience_evidence('I do not have 3 years of experience.')['status'], 'review')
        self.assertEqual(experience_evidence('2 years of experience.\nWork experience: 4 years')['status'], 'review')
        self.assertEqual(education_evidence('Master data management and Python tools.'), [])
        self.assertEqual(education_evidence('Education\nNo CA, 2024', accepted=['CA'])[0]['status'], 'review')
        self.assertEqual(education_evidence('Education\nB.Tech, 2024-2020')[0]['status'], 'review')

    def test_jd_reader_handles_ranges_freshers_and_absent_values(self):
        guessed = suggest_requirements(JOB)
        self.assertEqual(guessed['minimum_years'], 2)
        self.assertEqual(guessed['qualifications'], 'B.Tech')
        self.assertEqual(guessed['graduation_years'], '2023, 2024, 2025')
        self.assertEqual(suggest_requirements('No prior work experience required.')['minimum_years'], 0)
        self.assertIsNone(suggest_requirements('Python and SQL developer.')['minimum_years'])
        self.assertIsNone(suggest_requirements('Experience: 80 years')['minimum_years'])

    def test_settings_validation(self):
        for years in ['2025-2023', '2024 / 2025', 'any', 'abc']:
            with self.assertRaises(ValueError):
                make_requirements(0, 'B.Tech', years)
        for minimum in [-1, 61, float('nan')]:
            with self.assertRaises(ValueError):
                make_requirements(minimum, 'B.Tech')
        self.assertEqual(make_requirements(0, 'B.Tech, Bachelor of Technology', '2024, 2024-2025')['accepted_qualifications'], ['B.Tech'])
        self.assertEqual(make_requirements(0, 'be, btech')['accepted_qualifications'], ['B.E.', 'B.Tech'])

    def test_high_skill_match_cannot_clear_missing_details(self):
        result = analyze('Python developer with Python projects and software delivery skills.',
                         'Python developer needed for Python projects and software delivery.', requirements=self.cfg())
        self.assertEqual(result['skill_coverage'], 100)
        self.assertNotEqual(result['requirement_review']['summary'], 'Meets configured checks')

    def test_exports_include_requirements_and_evidence(self):
        result = analyze(RESUME, JOB, requirements=self.cfg())
        md = markdown_report(result)
        self.assertIn('Mandatory resume details', md)
        self.assertIn('At least 2 years', md)
        self.assertIn('Meets configured checks', md)
        pdf_text = '\n'.join(p.extract_text() for p in PdfReader(BytesIO(pdf_report(result))).pages)
        self.assertIn('Mandatory resume details', pdf_text)
        self.assertIn('At least 2 years', pdf_text)


class RequirementAppTests(unittest.TestCase):
    def test_read_jd_analyze_and_invalidate_changed_requirements(self):
        app = AppTest.from_file(APP).run(timeout=30)
        app.text_area(key='resume_text').set_value(RESUME).run()
        app.text_area(key='job_text').set_value(JOB).run()
        next(b for b in app.button if b.label == 'Read requirements from JD').click().run()
        self.assertEqual(app.number_input(key='required_years').value, 2)
        self.assertEqual(app.text_input(key='required_qualifications').value, 'B.Tech')
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['requirement_review']['summary'], 'Meets configured checks')
        app.number_input(key='required_years').set_value(4.0).run()
        self.assertEqual(len(app.metric), 0)
        self.assertFalse(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertEqual(app.session_state['result']['requirement_review']['summary'], 'Does not meet configured checks')

    def test_invalid_batch_setting_blocks_analysis_and_clear_resets(self):
        app = AppTest.from_file(APP).run(timeout=30)
        app.text_input(key='required_grad_years').set_value('2026-2024').run()
        self.assertTrue(app.error)
        self.assertTrue(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        next(b for b in app.button if b.label == 'Clear session').click().run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.number_input(key='required_years').value)
        self.assertEqual(app.text_input(key='required_grad_years').value, '')


if __name__ == '__main__':
    unittest.main()
