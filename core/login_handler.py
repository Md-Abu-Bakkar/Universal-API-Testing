"""
Login Handler - Handle authentication and session management
"""

import re
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class LoginHandler:
    def __init__(self, config=None):
        self.session = requests.Session()
        self.config = config or {}
        self.is_logged_in = False
        self.session_data = {}
        
        # Common login form patterns
        self.login_patterns = [
            r'<form[^>]*(login|signin|auth|authenticate)[^>]*>',
            r'<input[^>]*(username|email|user)[^>]*>',
            r'<input[^>]*(password|pass)[^>]*>',
            r'name=["\'](username|email|user|password|pass)["\']'
        ]
    
    def detect_mode(self, credentials: Dict[str, Any]) -> bool:
        """
        Detect if login mode should be used
        
        Args:
            credentials: Dictionary containing username, password, url
            
        Returns:
            bool: True if login mode should be used
        """
        has_credentials = credentials.get('username') and credentials.get('password')
        has_url = credentials.get('url')
        
        if not has_credentials or not has_url:
            logger.info("Insufficient credentials for login mode")
            return False
        
        # Check if URL is accessible and has login form
        try:
            response = self.session.get(credentials['url'], timeout=10)
            if self._has_login_form(response.text):
                logger.info("Login form detected, using login mode")
                return True
            else:
                logger.info("No login form detected, using direct mode")
                return False
        except Exception as e:
            logger.error(f"Error detecting login mode: {e}")
            return False
    
    def login_mode(self, credentials: Dict[str, Any]) -> Optional[requests.Session]:
        """
        Handle login-based authentication
        
        Args:
            credentials: Dictionary containing username, password, url
            
        Returns:
            requests.Session: Authenticated session or None if failed
        """
        logger.info(f"Attempting login to {credentials['url']}")
        
        max_attempts = self.config.get('login', {}).get('max_login_attempts', 3)
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Login attempt {attempt}/{max_attempts}")
                
                # Get login page to extract form data
                login_page = self.session.get(credentials['url'], timeout=10)
                
                # Extract login form details
                form_data = self._extract_login_form(login_page.text, credentials)
                if not form_data:
                    logger.error("Could not extract login form data")
                    continue
                
                # Solve captcha if present
                if self.config.get('login', {}).get('auto_captcha_solve', True):
                    form_data = self._solve_captcha(login_page.text, form_data)
                
                # Perform login
                login_url = form_data.get('action') or credentials['url']
                if not login_url.startswith(('http://', 'https://')):
                    login_url = urljoin(credentials['url'], login_url)
                
                login_response = self.session.post(
                    login_url,
                    data=form_data['fields'],
                    headers=form_data.get('headers', {}),
                    timeout=30,
                    allow_redirects=True
                )
                
                # Check if login was successful
                if self._is_login_successful(login_response, credentials['url']):
                    logger.info("Login successful!")
                    self.is_logged_in = True
                    
                    # Save session data
                    self.session_data = {
                        'cookies': dict(self.session.cookies),
                        'headers': dict(self.session.headers),
                        'login_time': time.time()
                    }
                    
                    return self.session
                else:
                    logger.warning(f"Login attempt {attempt} failed")
                    
            except Exception as e:
                logger.error(f"Login attempt {attempt} error: {e}")
            
            # Wait before retry
            if attempt < max_attempts:
                time.sleep(2)
        
        logger.error("All login attempts failed")
        return None
    
    def direct_api_mode(self, base_url: str) -> requests.Session:
        """
        Handle direct API testing without authentication
        
        Args:
            base_url: Base URL for API testing
            
        Returns:
            requests.Session: Session object
        """
        logger.info(f"Using direct API mode for {base_url}")
        
        # Set basic headers
        self.session.headers.update({
            'User-Agent': self.config.get('browser', {}).get('user_agent', 
                         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'),
            'Accept': 'application/json, text/plain, */*',
            'Referer': base_url
        })
        
        return self.session
    
    def _has_login_form(self, html: str) -> bool:
        """Check if HTML contains login form elements"""
        for pattern in self.login_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        return False
    
    def _extract_login_form(self, html: str, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract login form data from HTML"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find login form
            form = None
            for form_candidate in soup.find_all('form'):
                form_html = str(form_candidate).lower()
                if any(keyword in form_html for keyword in ['login', 'signin', 'auth', 'authenticate']):
                    form = form_candidate
                    break
            
            if not form:
                # Try to find any form with username and password fields
                for form_candidate in soup.find_all('form'):
                    input_fields = form_candidate.find_all('input')
                    has_username = any(field.get('name', '').lower() in ['username', 'email', 'user'] for field in input_fields)
                    has_password = any(field.get('type') == 'password' for field in input_fields)
                    
                    if has_username and has_password:
                        form = form_candidate
                        break
            
            if not form:
                return None
            
            # Extract form action
            action = form.get('action', '')
            method = form.get('method', 'post').upper()
            
            # Extract form fields
            fields = {}
            for input_field in form.find_all('input'):
                name = input_field.get('name')
                input_type = input_field.get('type', '').lower()
                value = input_field.get('value', '')
                
                if name:
                    if input_type == 'text' and any(keyword in name.lower() for keyword in ['user', 'email', 'name']):
                        fields[name] = credentials['username']
                    elif input_type == 'password':
                        fields[name] = credentials['password']
                    elif input_type in ['hidden', 'submit']:
                        fields[name] = value
            
            return {
                'action': action,
                'method': method,
                'fields': fields,
                'headers': {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': credentials['url']
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting login form: {e}")
            return None
    
    def _solve_captcha(self, html: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve captcha if present in the form"""
        try:
            # Look for math captcha (e.g., "What is 5 + 3?")
            math_patterns = [
                r'What is (\d+)\s*\+\s*(\d+)\s*\?',
                r'(\d+)\s*\+\s*(\d+)\s*=',
                r'captcha.*?(\d+).*?(\d+)'
            ]
            
            for pattern in math_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2))
                    answer = num1 + num2
                    
                    logger.info(f"Solved math captcha: {num1} + {num2} = {answer}")
                    
                    # Find captcha field in form
                    for field_name in form_data['fields']:
                        if 'captcha' in field_name.lower() or 'math' in field_name.lower():
                            form_data['fields'][field_name] = str(answer)
                            break
                    
                    break
            
            return form_data
            
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            return form_data
    
    def _is_login_successful(self, response, original_url: str) -> bool:
        """Check if login was successful"""
        # Check HTTP status
        if response.status_code not in [200, 302]:
            return False
        
        # Check for common login failure indicators
        failure_indicators = [
            'invalid', 'error', 'failed', 'incorrect', 'wrong',
            'login failed', 'invalid credentials', 'access denied'
        ]
        
        response_text = response.text.lower()
        if any(indicator in response_text for indicator in failure_indicators):
            return False
        
        # Check for success indicators
        success_indicators = [
            'dashboard', 'welcome', 'success', 'logged in',
            'logout', 'profile', 'account'
        ]
        
        if any(indicator in response_text for indicator in success_indicators):
            return True
        
        # Check if we were redirected away from login page
        if response.url != original_url and 'login' not in response.url.lower():
            return True
        
        # Check cookies for session indicators
        session_cookies = ['session', 'token', 'auth', 'loggedin']
        for cookie in self.session.cookies:
            if any(indicator in cookie.name.lower() for indicator in session_cookies):
                return True
        
        return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'is_logged_in': self.is_logged_in,
            'cookies': dict(self.session.cookies),
            'headers': dict(self.session.headers),
            'session_data': self.session_data
        }
    
    def logout(self):
        """Logout and clear session"""
        logger.info("Logging out and clearing session")
        self.session.close()
        self.is_logged_in = False
        self.session_data = {}
        self.session = requests.Session()
