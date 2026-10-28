import unittest
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest
from analyzer.core import analyze, markdown_report
from analyzer.requirements import make_requirements
from analyzer.reports import pdf_report
from analyzer.summary import report_summary

ROOT = Path(__file__).resolve().parents[1]
RESUME = (ROOT / 'samples/requirements_resume.txt').read_text()
JOB = (ROOT / 'samples/requirements_job.txt').read_text()


def button(app, label):
    return next(b for b in app.button if b.label == label)


class SummaryTests(unittest.TestCase):
    def test_missing_settings_distinct_from_missing_resume(self):
        result = analyze(RESUME, JOB)
        summary = result['summary']
        self.assertEqual(summary['missing_jd_settings'], ['minimum experience', 'accepted qualifications'])
        self.assertEqual(summary['missing_resume_details'], [])
        self.assertEqual(len(summary['top_actions']), 3)
        self.assertEqual(summary['status'], 'Needs review')

    def test_complete_checks_with_required_gap(self):
        result = analyze(RESUME.replace('SQL', 'Excel'), JOB, requirements=make_requirements(2, 'B.Tech'))
        self.assertEqual(result['summary']['status'], 'Required skill gaps to review')
        self.assertIn('SQL', result['summary']['required_gaps'])

    def test_no_skills_and_no_false_success(self):
        result = analyze(RESUME, 'We need a thoughtful person to join our friendly team and help out.', requirements=make_requirements(2, 'B.Tech'))
        self.assertEqual(result['skill_coverage'], None)
        self.assertEqual(result['summary']['job_skill_count'], 0)
        self.assertEqual(result['summary']['status'], 'Needs review: no JD skills detected')

    def test_exports_have_summary_and_correction_provenance(self):
        result = analyze(RESUME, JOB, requirements=make_requirements(2, 'B.Tech'))
        result['input_review'] = {'note': 'Analysis uses user-corrected preview text for: resume.'}
        summary = report_summary(result)
        md = markdown_report(result)
        pdf = PdfReader(BytesIO(pdf_report(result)))
        first = pdf.pages[0].extract_text()
        for text in ['At a glance', 'Your next three actions', 'user-corrected preview text', summary['status']]:
            self.assertIn(text, md)
            self.assertIn(text, first)
        self.assertIn('Mandatory resume details', pdf.pages[1].extract_text())


class PreviewTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        button(app, 'Try a sample analysis').click().run()
        return app

    def test_corrected_resume_changes_result_and_stale_detection(self):
        app = self.app()
        app.checkbox(key='edit_preview').check().run()
        original = app.text_area(key='resume_text').value
        app.text_area(key='preview_resume').set_value(original + '\nSkills: Excel, Statistics, Power BI, Communication, Data Visualization.').run()
        button(app, 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, '100.0%')
        self.assertEqual(app.session_state['result']['input_review']['corrected_documents'], ['resume'])
        self.assertEqual(app.text_area(key='resume_text').value, original)
        app.text_area(key='preview_resume').set_value(original).run()
        self.assertEqual(len(app.metric), 0)
        self.assertFalse(button(app, 'Analyze my match →').disabled)

    def test_corrected_jd_drives_suggestions_and_qualification_checks(self):
        app = self.app()
        app.checkbox(key='edit_preview').check().run()
        app.text_area(key='preview_resume').set_value(RESUME).run()
        app.text_area(key='preview_job').set_value(JOB).run()
        button(app, 'Read requirements from JD').click().run()
        self.assertEqual(app.number_input(key='required_years').value, 2.0)
        button(app, 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['requirement_review']['summary'], 'Meets configured checks')
        self.assertEqual(app.session_state['result']['input_review']['corrected_documents'], ['resume', 'JD'])

    def test_reset_toggle_and_document_change(self):
        app = self.app()
        original = app.text_area(key='resume_text').value
        app.checkbox(key='edit_preview').check().run()
        app.text_area(key='preview_resume').set_value(RESUME).run()
        button(app, 'Reset preview to original documents').click().run()
        self.assertEqual(app.text_area(key='preview_resume').value, original)
        app.text_area(key='preview_resume').set_value(RESUME).run()
        app.checkbox(key='edit_preview').uncheck().run()
        button(app, 'Analyze my match →').click().run(timeout=30)
        self.assertEqual(app.session_state['result']['input_review']['corrected_documents'], [])
        app.text_area(key='resume_text').set_value(RESUME).run()
        self.assertFalse(app.checkbox(key='edit_preview').value)
        app.checkbox(key='edit_preview').check().run()
        self.assertEqual(app.text_area(key='preview_resume').value, RESUME)

    def test_uploaded_text_can_be_corrected(self):
        app = self.app()
        app.radio(key='source').set_value('Upload file').run()
        app.file_uploader[0].upload('resume.txt', RESUME.encode(), 'text/plain').run()
        app.checkbox(key='edit_preview').check().run()
        self.assertEqual(app.text_area(key='preview_resume').value.strip(), RESUME.strip())
        app.text_area(key='preview_resume').set_value(RESUME + '\nSkills: Excel.').run()
        button(app, 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertIn('Excel', app.session_state['result']['matched_skills'])


if __name__ == '__main__':
    unittest.main()
