"""
Tests for API Scanner module
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api_scanner import APIScanner

class TestAPIScanner(unittest.TestCase):
    """Test cases for APIScanner"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scanner = APIScanner()
        self.sample_devtools_data = """
        GET https://api.example.com/v1/users
        POST https://api.example.com/v1/login
        https://api.example.com/v1/data.json
        """
    
    def test_extract_apis_basic(self):
        """Test basic API extraction"""
        apis = self.scanner.extract_apis(self.sample_devtools_data)
        
        self.assertGreater(len(apis), 0)
        
        # Check if URLs are extracted
        urls = [api['url'] for api in apis]
        self.assertIn('https://api.example.com/v1/users', urls)
        self.assertIn('https://api.example.com/v1/login', urls)
    
    def test_extract_apis_empty(self):
        """Test API extraction with empty data"""
        apis = self.scanner.extract_apis("")
        self.assertEqual(len(apis), 0)
    
    def test_api_classification(self):
        """Test API classification"""
        test_cases = [
            ('https://api.example.com/v1/sms', 'SMS'),
            ('https://api.example.com/login', 'AUTH'),
            ('https://api.example.com/api/data', 'API'),
            ('https://example.com/graphql', 'GRAPHQL'),
            ('https://example.com/ajax/data', 'AJAX')
        ]
        
        for url, expected_type in test_cases:
            api_info = self.scanner._analyze_api_url(url)
            self.assertEqual(api_info['type'], expected_type)
    
    def test_priority_calculation(self):
        """Test API priority calculation"""
        high_priority_urls = [
            'https://api.example.com/v1/sms',
            'https://api.example.com/data_sms',
            'https://api.example.com/api/messages'
        ]
        
        for url in high_priority_urls:
            api_info = self.scanner._analyze_api_url(url)
            self.assertEqual(api_info['priority'], 3)
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            'https://api.example.com/v1/data',
            'http://localhost:8000/api',
            'https://example.com/data.json'
        ]
        
        invalid_urls = [
            'https://example.com/style.css',
            'https://fonts.googleapis.com/css',
            'https://example.com/script.js'
        ]
        
        for url in valid_urls:
            self.assertTrue(self.scanner._is_valid_api_url(url))
        
        for url in invalid_urls:
            self.assertFalse(self.scanner._is_valid_api_url(url))
    
    def test_method_detection(self):
        """Test HTTP method detection"""
        test_cases = [
            ('https://api.example.com/login', 'POST'),
            ('https://api.example.com/users', 'GET'),
            ('https://api.example.com/update', 'PUT'),
            ('https://api.example.com/delete', 'DELETE')
        ]
        
        for url, expected_method in test_cases:
            api_info = self.scanner._analyze_api_url(url)
            self.assertEqual(api_info['method'], expected_method)

if __name__ == '__main__':
    unittest.main()
