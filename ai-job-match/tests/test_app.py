import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


class AppTests(unittest.TestCase):
    def test_sample_analyze_export_and_stale_state(self):
        app = AppTest.from_file(APP).run(timeout=30)
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, '44.4%')
        self.assertEqual(app.metric[2].value, '5')
        self.assertEqual(len(app.get('download_button')), 4)
        self.assertEqual(app.metric[3].value, '50.0%')
        self.assertEqual(app.metric[4].value, '33.3%')
        self.assertTrue(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        app.text_area(key='job_text').set_value('A different job requiring Docker, Linux and Kubernetes for cloud systems.').run()
        self.assertFalse(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any('changed' in i.value for i in app.info))

    def test_validation_and_clear(self):
        app = AppTest.from_file(APP).run(timeout=30)
        next(b for b in app.button if b.label == 'Analyze my match →').click().run()
        self.assertTrue(app.error)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        next(b for b in app.button if b.label == 'Clear session').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_area(key='resume_text').value, '')

    def test_upload_flow(self):
        app = AppTest.from_file(APP).run(timeout=30)
        app.radio(key='source').set_value('Upload file').run()
        text = 'Python SQL Pandas developer with data analysis and Git project experience.'
        app.file_uploader[0].upload('resume.txt', text.encode(), 'text/plain').run()
        app.text_area(key='job_text').set_value('Looking for Python SQL and Excel skills for a data analysis project.').run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value, '1')

    def test_ai_failure_is_visible(self):
        app = AppTest.from_file(APP).run(timeout=30)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        app.radio(key='engine').set_value('AI · Sentence Transformers').run()
        with patch('analyzer.core.load_model', side_effect=RuntimeError('Model unavailable')):
            next(b for b in app.button if b.label == 'Analyze my match →').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('could not start' in e.value for e in app.error))
        self.assertEqual(len(app.metric), 0)

    def test_job_upload_and_sample_reset(self):
        app = AppTest.from_file(APP).run(timeout=30)
        app.text_area(key='resume_text').set_value('Python SQL Pandas developer with data analysis and Git project experience.').run()
        app.radio(key='job_source').set_value('Upload file').run()
        app.file_uploader[0].upload('job.txt', b'Looking for Python SQL and Excel skills for a data analysis project.', 'text/plain').run()
        next(b for b in app.button if b.label == 'Analyze my match →').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value, '1')
        self.assertTrue(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        self.assertEqual(app.radio(key='job_source').value, 'Paste text')
        self.assertEqual(len(app.metric), 0)

    def test_invalid_job_upload_blocks_analysis(self):
        app = AppTest.from_file(APP).run(timeout=30)
        next(b for b in app.button if b.label == 'Try a sample analysis').click().run()
        app.radio(key='job_source').set_value('Upload file').run()
        app.file_uploader[0].upload('broken.pdf', b'not a PDF', 'application/pdf').run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertTrue(next(b for b in app.button if b.label == 'Analyze my match →').disabled)
        self.assertEqual(len(app.metric), 0)


if __name__ == '__main__':
    unittest.main()
