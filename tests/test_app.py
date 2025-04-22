# tests/test_app.py
import unittest
import os
import io
from PIL import Image
from app import app
from app import app


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)



class FlaskExifTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a test image with EXIF data
        self.test_image = Image.new('RGB', (100, 100))
        self.exif_data = {
            'ImageDescription': 'Test Image',
            'Make': 'Test Camera',
            'Model': 'Test Model',
            'DateTime': '2023:01:01 12:00:00',
            'GPSInfo': {1: 'N', 2: ((37, 1), (42, 1), (12, 1)), 3: 'W', 4: ((122, 1), (24, 1), (36, 1))}
        }
        self.test_image.info['exif'] = self.exif_data
        
        # Save to bytes for testing upload
        self.img_byte_arr = io.BytesIO()
        self.test_image.save(self.img_byte_arr, format='JPEG', exif=self.exif_data)
        self.img_byte_arr.seek(0)

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('EXIF Data Viewer'.encode('utf-8'), response.data)

    def test_upload_page(self):
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Upload Image'.encode('utf-8'), response.data)

    def test_image_upload(self):
        data = {
            'file': (self.img_byte_arr, 'test_image.jpg')
        }
        response = self.app.post('/upload', 
                               data=data,
                               content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('EXIF Data'.encode('utf-8'), response.data)

    def test_exif_data_display(self):
        data = {
            'file': (self.img_byte_arr, 'test_image.jpg')
        }
        response = self.app.post('/upload', 
                               data=data,
                               content_type='multipart/form-data')
        
        # Check if EXIF data is displayed correctly
        self.assertIn('Test Image'.encode('utf-8'), response.data)  # ImageDescription
        self.assertIn('Test Camera'.encode('utf-8'), response.data)  # Make
        self.assertIn('Test Model'.encode('utf-8'), response.data)  # Model
        self.assertIn('2023:01:01 12:00:00'.encode('utf-8'), response.data)  # DateTime

    def test_gps_data_display(self):
        data = {
            'file': (self.img_byte_arr, 'test_image.jpg')
        }
        response = self.app.post('/upload', 
                               data=data,
                               content_type='multipart/form-data')
        
        # Check if GPS data is processed and displayed
        # Using encoded strings instead of special characters
        self.assertIn('N'.encode('utf-8'), response.data)  # Latitude direction
        self.assertIn('W'.encode('utf-8'), response.data)  # Longitude direction
        self.assertIn('37.0'.encode('utf-8'), response.data)  # Latitude degrees
        self.assertIn('122.0'.encode('utf-8'), response.data)  # Longitude degrees

    def test_invalid_file_upload(self):
        # Test with non-image file
        data = {
            'file': (io.BytesIO(b'not an image'), 'test.txt')
        }
        response = self.app.post('/upload', 
                               data=data,
                               content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file format'.encode('utf-8'), response.data)

    def test_no_file_upload(self):
        # Test with no file selected
        response = self.app.post('/upload', 
                               data={},
                               content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file selected'.encode('utf-8'), response.data)

    def test_image_without_exif(self):
        # Create image without EXIF data
        img_no_exif = Image.new('RGB', (100, 100))
        img_byte_arr = io.BytesIO()
        img_no_exif.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        data = {
            'file': (img_byte_arr, 'no_exif.jpg')
        }
        response = self.app.post('/upload', 
                               data=data,
                               content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No EXIF data found'.encode('utf-8'), response.data)

    def test_exif_data_api(self):
        # If you have an API endpoint for EXIF data
        data = {
            'file': (self.img_byte_arr, 'test_image.jpg')
        }
        response = self.app.post('/api/exif', 
                               data=data,
                               content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Image'.encode('utf-8'), response.data)
        self.assertIn('Test Camera'.encode('utf-8'), response.data)
        
        # Check if response is JSON
        self.assertTrue(response.is_json)

    def tearDown(self):
        # Clean up any test files if needed
        pass