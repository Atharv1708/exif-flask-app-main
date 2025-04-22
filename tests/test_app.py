import unittest
import os
import tempfile
from app import app

class FlaskExifTestCase(unittest.TestCase):
    def setUp(self):
        # Configure test upload folder
        self.upload_folder = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = self.upload_folder
        app.config['TESTING'] = True
        
        self.app = app.test_client()
        
        # Create a test file
        self.test_file = os.path.join(self.upload_folder, 'test.jpg')
        with open(self.test_file, 'wb') as f:
            f.write(b'Test file content')

    def tearDown(self):
        # Clean up test files
        for filename in os.listdir(self.upload_folder):
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.upload_folder)

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('File Metadata Extractor', response_text)

    def test_file_upload(self):
        with open(self.test_file, 'rb') as f:
            response = self.app.post(
                '/',
                data={'file': (f, 'test.jpg')},
                content_type='multipart/form-data'
            )
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('Extracted Metadata', response_text)

    def test_invalid_file_upload(self):
        response = self.app.post(
            '/',
            data={'file': (io.BytesIO(b'not an image'), 'test.txt'},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        response_text = response.data.decode('utf-8')
        self.assertIn('Invalid file format', response_text)

    def test_no_file_upload(self):
        response = self.app.post('/', data={})
        self.assertEqual(response.status_code, 400)
        response_text = response.data.decode('utf-8')
        self.assertIn('No file selected', response_text)
