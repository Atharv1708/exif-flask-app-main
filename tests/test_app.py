import unittest
import os
import io
from app import app

class FlaskAppBasicTests(unittest.TestCase):
    def setUp(self):
        # Configure test client
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        self.app = app.test_client()
        
        # Create test upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def tearDown(self):
        # Clean up test upload directory
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(app.config['UPLOAD_FOLDER'])

    def test_home_page(self):
        """Test that home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File Metadata Extractor', response.data)

    def test_file_upload(self):
        """Test valid file upload"""
        # Create a test file
        test_file = (io.BytesIO(b'fake image data'), 'test.jpg')
        
        response = self.app.post(
            '/',
            data={'file': test_file},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Extracted Metadata', response.data)

    def test_invalid_file_upload(self):
        """Test invalid file upload"""
        response = self.app.post(
            '/',
            data={'file': (io.BytesIO(b'not an image'), 'test.txt')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid file format', response.data)

    def test_no_file_upload(self):
        """Test submission with no file"""
        response = self.app.post('/', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file selected', response.data)

if __name__ == '__main__':
    unittest.main()
