import unittest
import os
from io import BytesIO
from app import app
import atexit

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.test_upload_dir = 'test_uploads'
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = self.test_upload_dir

        # Prevent atexit cleanup from running during tests
        if hasattr(atexit, '_exithandlers'):
            atexit._exithandlers.clear()

        os.makedirs(self.test_upload_dir, exist_ok=True)
        self.client = app.test_client()

    def tearDown(self):
        for f in os.listdir(self.test_upload_dir):
            os.remove(os.path.join(self.test_upload_dir, f))
        os.rmdir(self.test_upload_dir)

    def test_get_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EXIF Data Extractor', response.data)

    def test_post_image_with_exif(self):
        image_data = BytesIO()
        image_data.write(b'\xff\xd8\xff\xe1Exif' + b'\x00' * 100)
        image_data.seek(0)
        response = self.client.post(
            '/',
            data={'file': (image_data, 'test.jpg')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No EXIF data found.', response.data)

    def test_post_invalid_file_type(self):
        fake_file = BytesIO(b'not an image')
        response = self.client.post(
            '/',
            data={'file': (fake_file, 'badfile.txt')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file format.', response.data)

    def test_post_video_file(self):
        fake_video = BytesIO(b'\x00' * 1024)
        response = self.client.post(
            '/',
            data={'file': (fake_video, 'test.mp4')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No video metadata found.', response.data)

if _name_ == '_main_':
    unittest.main()
