import unittest
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from analyzer.core import analyze, skill_context, markdown_report
from analyzer.reports import pdf_report

ROOT = Path(__file__).resolve().parents[1]


class ContextTests(unittest.TestCase):
    def test_list_suffixes_and_learning_headings(self):
        found = skill_context('Python and SQL not required. Git and Docker preferred.', job=True)
        self.assertEqual(found['Python']['status'], 'excluded')
        self.assertEqual(found['SQL']['status'], 'excluded')
        self.assertEqual(found['Git']['status'], 'preferred')
        found = skill_context('Currently learning:\nPython, SQL\nProjects:\nBuilt with Git and Docker.')
        self.assertEqual(found['Python']['status'], 'learning')
        self.assertEqual(found['SQL']['status'], 'learning')
        self.assertEqual(found['Git']['status'], 'mentioned')

    def test_machine_learning_is_not_a_learning_context_cue(self):
        found = skill_context('Machine Learning, Deep Learning, Git, HTML and CSS.')
        self.assertTrue(all(entry['status'] == 'mentioned' for entry in found.values()))

    def test_resume_negation_learning_and_positive_clause(self):
        found = skill_context('No experience with Python and SQL, but experienced in Git. Currently learning Docker.')
        self.assertEqual(found['Python']['status'], 'negated')
        self.assertEqual(found['SQL']['status'], 'negated')
        self.assertEqual(found['Git']['status'], 'mentioned')
        self.assertEqual(found['Docker']['status'], 'learning')

    def test_conflicting_mentions_require_review(self):
        found = skill_context('No experience in Python. Built with Python last year.')
        self.assertEqual(found['Python']['status'], 'review')
        self.assertEqual(len(found['Python']['mentions']), 2)

    def test_priorities_headings_inline_and_exclusions(self):
        text = 'Required skills:\nPython and SQL\nPreferred skills:\nGit and Docker\nResponsibilities:\nExcel reports. Kubernetes is not required.'
        found = skill_context(text, job=True)
        self.assertEqual(found['Python']['status'], 'required')
        self.assertEqual(found['SQL']['status'], 'required')
        self.assertEqual(found['Git']['status'], 'preferred')
        self.assertEqual(found['Docker']['status'], 'preferred')
        self.assertEqual(found['Excel']['status'], 'unspecified')
        self.assertEqual(found['Kubernetes']['status'], 'excluded')
        found = skill_context('Python required, Docker preferred. SQL is a plus.', job=True)
        self.assertEqual(found['Python']['status'], 'required')
        self.assertEqual(found['Docker']['status'], 'preferred')
        self.assertEqual(found['SQL']['status'], 'preferred')

    def test_strongest_requirement_and_positive_evidence(self):
        resume = 'Learning Python. No experience with SQL. Experienced in Git and project delivery.'
        job = 'Preferred: Python and Git.\nRequired: Python and SQL. Docker not required.'
        result = analyze(resume, job)
        self.assertEqual(result['matched_skills'], ['Git'])
        self.assertEqual(result['required_coverage'], 0)
        self.assertEqual(result['preferred_coverage'], 100)
        self.assertIn('Docker', result['excluded_job_skills'])
        self.assertEqual(result['learning_plan'][0]['priority'], 'required')
        self.assertEqual(result['learning_plan'][0]['resume_status'], 'learning')
        self.assertTrue(result['learning_plan'][0]['resource_url'].startswith('https://docs.python.org/'))

    def test_all_excluded_gives_na(self):
        result = analyze('Experienced developer with many projects and a clear portfolio.',
                         'Python is not required. SQL is not required for this position.')
        self.assertIsNone(result['skill_coverage'])
        self.assertIsNone(result['required_coverage'])
        self.assertFalse(result['learning_plan'])

    def test_custom_skill_fallback_and_plan_order(self):
        result = analyze('Experienced developer building Python projects and documenting the results.',
                         'Preferred: SQL.\nRequired: Figma.\nResponsibilities: Excel reports.', custom=['Figma'])
        self.assertEqual([s['skill'] for s in result['learning_plan']], ['Figma', 'Excel', 'SQL'])
        self.assertIsNone(result['learning_plan'][0]['resource_url'])
        self.assertIn('No curated link', result['learning_plan'][0]['resource_note'])


class ReportTests(unittest.TestCase):
    def sample(self):
        return analyze((ROOT / 'samples/resume.txt').read_text(), (ROOT / 'samples/job_description.txt').read_text())

    def test_pdf_and_markdown_include_priorities_and_resources(self):
        result = self.sample()
        data = pdf_report(result)
        self.assertTrue(data.startswith(b'%PDF'))
        reader = PdfReader(BytesIO(data))
        text = '\n'.join(p.extract_text() for p in reader.pages)
        for term in ['44.4%', 'Required', 'Preferred', 'Practice plan', 'https://support.microsoft.com/en-us/excel/', 'Limitations']:
            self.assertIn(term, text)
        md = markdown_report(result)
        self.assertIn('### Required', md)
        self.assertIn('50.0%', md)
        self.assertIn('https://support.microsoft.com/en-us/excel/', md)

    def test_pdf_escapes_markup_and_wraps_long_evidence(self):
        result = self.sample()
        result['evidence'][0]['resume_evidence'] = '<b>literal & safe</b> ' + 'longword' * 70 + ' café résumé'
        data = pdf_report(result)
        text = '\n'.join(p.extract_text() for p in PdfReader(BytesIO(data)).pages)
        self.assertIn('<b>literal & safe</b>', text)
        self.assertIn('café résumé', text)
        self.assertIn('Page 1', text)


if __name__ == '__main__':
    unittest.main()
