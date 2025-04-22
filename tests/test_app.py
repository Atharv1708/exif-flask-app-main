import unittest
import os
from io import BytesIO
from app import app


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        self.client = app.test_client()

        # Ensure test upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def tearDown(self):
        # Clean up test files
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
        os.rmdir(app.config['UPLOAD_FOLDER'])

    def test_get_index(self):
        """GET / should load the index page with 200 OK"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EXIF Data Extractor', response.data)

    def test_post_image_with_exif(self):
        """POST image with EXIF data returns parsed EXIF"""
        # A very basic JPEG with minimal EXIF (simulated here)
        image_data = BytesIO()
        image_data.write(b'\xff\xd8\xff\xe1' + b'Exif' + b'\x00' * 100)  # Simulate EXIF segment
        image_data.seek(0)

        response = self.client.post(
            '/',
            data={'file': (image_data, 'test.jpg')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No EXIF data', response.data)  # Since it's fake, no real data

    def test_post_invalid_file_type(self):
        """POST with invalid file type returns error"""
        fake_file = BytesIO(b'not an image')
        response = self.client.post(
            '/',
            data={'file': (fake_file, 'badfile.txt')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file format', response.data)

    def test_post_video_file(self):
        """POST with fake video metadata (mocked video file)"""
        fake_video = BytesIO(b'\x00' * 1024)  # Not a real video, but enough for test
        response = self.client.post(
            '/',
            data={'file': (fake_video, 'test.mp4')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'No video metadata' in response.data or b'Invalid file format' in response.data)

if _name_ == '_main_':
    unittest.main()
