import unittest
from app import app

class TestIndexPage(unittest.TestCase):
    def setUp(self):
        # Create test client
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_index_page_loads(self):
        """Test that the index page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, 
                        "Index page should return status code 200")
        
        # Optional: Check for some expected text in the page
        self.assertIn(b'File Metadata Extractor', response.data,
                     "Page should contain 'File Metadata Extractor'")

if __name__ == '__main__':
    unittest.main()
