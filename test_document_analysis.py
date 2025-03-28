import os
import io
import unittest
from app import app, db
from models import User, ApiKey
from flask import session
from werkzeug.security import generate_password_hash

class DocumentAnalysisTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create a test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                is_admin=True,
                is_approved=True
            )
            db.session.add(test_user)
            
            # Add mock API key
            api_key = ApiKey(
                service_name='openai',
                key_value='test-api-key',
                created_by=1
            )
            db.session.add(api_key)
            db.session.commit()
            
            # Set environment variable for testing
            os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login(self):
        return self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
    
    def test_document_analysis_page_access(self):
        # Login first
        self.login()
        
        # Try to access the document analysis page
        response = self.client.get('/document-analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Document Analysis', response.data)
    
    def test_analyze_document_api_no_file(self):
        # Login first
        self.login()
        
        # Try to call the API without a file
        response = self.client.post('/api/analyze-document')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No file uploaded')
    
    def test_analyze_document_api_empty_file(self):
        # Login first
        self.login()
        
        # Try to call the API with an empty file
        response = self.client.post('/api/analyze-document', data={
            'file': (io.BytesIO(b''), '')
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No file selected')
    
    def test_analyze_document_api_invalid_format(self):
        # Login first
        self.login()
        
        # Try to call the API with an invalid file format
        response = self.client.post('/api/analyze-document', data={
            'file': (io.BytesIO(b'test data'), 'test.csv')
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid file format', data['message'])
    
    def test_analyze_document_api_txt_file(self):
        # Login first
        self.login()
        
        # Create a simple text file
        txt_content = b'This is a simple test document.\nIt has multiple lines.\nWe want to analyze it.'
        
        # Try to call the API with a valid text file
        response = self.client.post('/api/analyze-document', data={
            'file': (io.BytesIO(txt_content), 'test.txt')
        }, content_type='multipart/form-data')
        
        # Since we're using a mock API key, we don't expect a real analysis
        # but we can check that the API correctly handles the file
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # In testing mode, we should still get a response structure
        # even if it contains error messages due to mock API key
        self.assertIn('success', data)

if __name__ == '__main__':
    unittest.main()