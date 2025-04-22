import unittest
from app import app

class TestIndexPage(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_page_loads(self):
        """Test that index page loads successfully and contains main heading"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Check that the response includes the main title from index.html
        self.assertIn(b'EXIF Data Extractor', response.data)

if _name_ == '_main_':
    unittest.main()
