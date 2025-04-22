import unittest
from app import app

class TestIndexPage(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

 def test_index_page_loads(self):
    response = self.client.get('/')
    assert response.status_code == 200

        
        # Update this to match your actual page content:
        self.assertIn(b'Your Expected Page Title', response.data)

if __name__ == '__main__':
    unittest.main()
