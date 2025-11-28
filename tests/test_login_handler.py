"""
Tests for Login Handler module
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.login_handler import LoginHandler

class TestLoginHandler(unittest.TestCase):
    """Test cases for LoginHandler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.login_handler = LoginHandler()
    
    def test_detect_mode_with_credentials(self):
        """Test login mode detection with credentials"""
        credentials = {
            'username': 'testuser',
            'password': 'testpass',
            'url': 'https://example.com'
        }
        
        # This will return False in tests since we can't actually check for login forms
        # but we're testing the logic structure
        result = self.login_handler.detect_mode(credentials)
        self.assertIsInstance(result, bool)
    
    def test_detect_mode_without_credentials(self):
        """Test login mode detection without credentials"""
        credentials = {
            'username': '',
            'password': '',
            'url': 'https://example.com'
        }
        
        result = self.login_handler.detect_mode(credentials)
        self.assertFalse(result)
    
    def test_math_captcha_solving(self):
        """Test math captcha solving"""
        html_with_captcha = """
        <form>
            <label>What is 5 + 3? </label>
            <input type="text" name="captcha">
        </form>
        """
        
        form_data = {
            'fields': {
                'username': 'test',
                'password': 'test',
                'captcha': ''
            }
        }
        
        solved_form = self.login_handler._solve_captcha(html_with_captcha, form_data)
        self.assertEqual(solved_form['fields']['captcha'], '8')
    
    def test_login_form_extraction(self):
        """Test login form extraction from HTML"""
        html_with_form = """
        <form action="/login" method="post">
            <input type="text" name="username" value="">
            <input type="password" name="password">
            <input type="hidden" name="csrf" value="abc123">
            <input type="submit" value="Login">
        </form>
        """
        
        credentials = {
            'username': 'testuser',
            'password': 'testpass',
            'url': 'https://example.com'
        }
        
        form_data = self.login_handler._extract_login_form(html_with_form, credentials)
        
        self.assertIsNotNone(form_data)
        self.assertEqual(form_data['action'], '/login')
        self.assertEqual(form_data['method'], 'POST')
        self.assertIn('username', form_data['fields'])
        self.assertIn('password', form_data['fields'])
        self.assertEqual(form_data['fields']['username'], 'testuser')
        self.assertEqual(form_data['fields']['password'], 'testpass')
    
    def test_has_login_form_detection(self):
        """Test login form detection"""
        html_with_login = """
        <form id="login-form">
            <input type="text" name="user">
            <input type="password" name="pass">
        </form>
        """
        
        html_without_login = """
        <form>
            <input type="text" name="search">
            <input type="submit" value="Search">
        </form>
        """
        
        self.assertTrue(self.login_handler._has_login_form(html_with_login))
        self.assertFalse(self.login_handler._has_login_form(html_without_login))

if __name__ == '__main__':
    unittest.main()
