import unittest
import os
import tempfile
from app import app

class FlaskExifTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Create temporary upload directory
        self.upload_folder = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = self.upload_folder

    def tearDown(self):
        # Clean up uploaded files
        for filename in os.listdir(self.upload_folder):
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.upload_folder)

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('EXIF Data Viewer', response_text)

    # Update all other test methods to use decode('utf-8') on response.data
    # Example:
    def test_upload_page(self):
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('Upload Image', response_text)
