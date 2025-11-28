"""
Request Parser - Parse and analyze HTTP requests from various formats
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import base64

logger = logging.getLogger(__name__)

class RequestParser:
    """Parse HTTP requests from different formats"""
    
    def __init__(self):
        self.supported_formats = ['curl', 'raw', 'har', 'devtools']
    
    def parse_curl(self, curl_command: str) -> Optional[Dict[str, Any]]:
        """
        Parse cURL command into request components
        
        Args:
            curl_command: cURL command string
            
        Returns:
            dict: Parsed request components
        """
        try:
            result = {
                'method': 'GET',
                'url': '',
                'headers': {},
                'data': None,
                'cookies': {}
            }
            
            # Extract URL
            url_match = re.search(r"curl\s+['\"]([^'\"]+)['\"]", curl_command)
            if not url_match:
                url_match = re.search(r'curl\s+([^\s]+)', curl_command)
            
            if url_match:
                result['url'] = url_match.group(1)
            
            # Extract method
            if '-X' in curl_command or '--request' in curl_command:
                method_match = re.search(r'-(?:X|-\w*request)\s+(\w+)', curl_command)
                if method_match:
                    result['method'] = method_match.group(1).upper()
            
            # Extract headers
            header_matches = re.findall(r"-(?:H|-\w*header)\s+['\"]([^'\"]+)['\"]", curl_command)
            for header in header_matches:
                if ':' in header:
                    key, value = header.split(':', 1)
                    result['headers'][key.strip()] = value.strip()
            
            # Extract data
            if '-d' in curl_command or '--data' in curl_command:
                data_match = re.search(r"-(?:d|-\w*data)\s+['\"]([^'\"]+)['\"]", curl_command)
                if data_match:
                    result['data'] = data_match.group(1)
                    if result['method'] == 'GET':
                        result['method'] = 'POST'
            
            # Extract cookies
            if '-b' in curl_command or '--cookie' in curl_command:
                cookie_match = re.search(r"-(?:b|-\w*cookie)\s+['\"]([^'\"]+)['\"]", curl_command)
                if cookie_match:
                    cookies = cookie_match.group(1)
                    for cookie in cookies.split(';'):
                        if '=' in cookie:
                            key, value = cookie.split('=', 1)
                            result['cookies'][key.strip()] = value.strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing cURL command: {e}")
            return None
    
    def parse_raw_request(self, raw_request: str) -> Optional[Dict[str, Any]]:
        """
        Parse raw HTTP request
        
        Args:
            raw_request: Raw HTTP request string
            
        Returns:
            dict: Parsed request components
        """
        try:
            lines = raw_request.strip().split('\n')
            if not lines:
                return None
            
            result = {
                'method': 'GET',
                'url': '',
                'headers': {},
                'data': None,
                'version': 'HTTP/1.1'
            }
            
            # Parse request line
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) >= 2:
                result['method'] = parts[0]
                result['url'] = parts[1]
                if len(parts) >= 3:
                    result['version'] = parts[2]
            
            # Parse headers
            data_start = None
            for i, line in enumerate(lines[1:], 1):
                if not line.strip():  # Empty line indicates end of headers
                    data_start = i + 1
                    break
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    result['headers'][key.strip()] = value.strip()
            
            # Parse data
            if data_start and data_start < len(lines):
                result['data'] = '\n'.join(lines[data_start:])
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing raw request: {e}")
            return None
    
    def parse_har(self, har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse HAR (HTTP Archive) data
        
        Args:
            har_data: HAR JSON data
            
        Returns:
            list: List of parsed requests
        """
        try:
            requests = []
            
            # Navigate to entries
            entries = har_data.get('log', {}).get('entries', [])
            
            for entry in entries:
                request_data = entry.get('request', {})
                response_data = entry.get('response', {})
                
                request = {
                    'method': request_data.get('method', 'GET'),
                    'url': request_data.get('url', ''),
                    'headers': {},
                    'cookies': {},
                    'post_data': request_data.get('postData'),
                    'response_status': response_data.get('status'),
                    'response_size': response_data.get('content', {}).get('size', 0)
                }
                
                # Parse headers
                for header in request_data.get('headers', []):
                    request['headers'][header['name']] = header['value']
                
                # Parse cookies
                for cookie in request_data.get('cookies', []):
                    request['cookies'][cookie['name']] = cookie['value']
                
                requests.append(request)
            
            return requests
            
        except Exception as e:
            logger.error(f"Error parsing HAR data: {e}")
            return []
    
    def parse_devtools_network(self, devtools_data: str) -> List[Dict[str, Any]]:
        """
        Parse Chrome DevTools network data
        
        Args:
            devtools_data: DevTools network export
            
        Returns:
            list: List of parsed requests
        """
        try:
            requests = []
            lines = devtools_data.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Try to extract URL from various formats
                url_patterns = [
                    r'https?://[^\s]+',
                    r'\"url\"\s*:\s*\"([^\"]+)\"',
                    r'GET\s+([^\s]+)',
                    r'POST\s+([^\s]+)'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, line)
                    for url in matches:
                        if self._is_valid_url(url):
                            request = {
                                'url': url,
                                'method': self._detect_method(line),
                                'headers': self._extract_headers(line),
                                'type': self._classify_request(url)
                            }
                            requests.append(request)
            
            return requests
            
        except Exception as e:
            logger.error(f"Error parsing DevTools data: {e}")
            return []
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from arbitrary text
        
        Args:
            text: Input text
            
        Returns:
            list: List of extracted URLs
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Filter valid URLs
        valid_urls = []
        for url in urls:
            if self._is_valid_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def analyze_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze request and extract metadata
        
        Args:
            request: Request data
            
        Returns:
            dict: Analysis results
        """
        analysis = {
            'url': request.get('url', ''),
            'method': request.get('method', 'GET'),
            'domain': '',
            'path': '',
            'query_params': {},
            'headers_count': len(request.get('headers', {})),
            'has_auth': False,
            'has_cookies': bool(request.get('cookies')),
            'content_type': '',
            'user_agent': '',
            'potential_api': False
        }
        
        # Parse URL
        try:
            parsed = urlparse(request['url'])
            analysis['domain'] = parsed.netloc
            analysis['path'] = parsed.path
            
            # Parse query parameters
            if parsed.query:
                analysis['query_params'] = parse_qs(parsed.query)
        except:
            pass
        
        # Analyze headers
        headers = request.get('headers', {})
        for key, value in headers.items():
            key_lower = key.lower()
            
            if key_lower == 'authorization':
                analysis['has_auth'] = True
            elif key_lower == 'content-type':
                analysis['content_type'] = value
            elif key_lower == 'user-agent':
                analysis['user_agent'] = value
        
        # Detect potential API
        analysis['potential_api'] = self._is_potential_api(request)
        
        return analysis
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _detect_method(self, text: str) -> str:
        """Detect HTTP method from text"""
        text_upper = text.upper()
        
        if 'POST' in text_upper:
            return 'POST'
        elif 'PUT' in text_upper:
            return 'PUT'
        elif 'DELETE' in text_upper:
            return 'DELETE'
        elif 'PATCH' in text_upper:
            return 'PATCH'
        else:
            return 'GET'
    
    def _extract_headers(self, text: str) -> Dict[str, str]:
        """Extract headers from text"""
        headers = {}
        
        # Look for header patterns
        header_patterns = [
            r'([^:]+):\s*([^\n]+)',
            r'"headers"\s*:\s*\{[^}]+\}',
        ]
        
        for pattern in header_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if ':' in match.group():
                    key, value = match.group().split(':', 1)
                    headers[key.strip()] = value.strip()
        
        return headers
    
    def _classify_request(self, url: str) -> str:
        """Classify request type based on URL"""
        url_lower = url.lower()
        
        if any(ext in url_lower for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico']):
            return 'static'
        elif any(keyword in url_lower for keyword in ['api', 'rest', 'graphql']):
            return 'api'
        elif any(keyword in url_lower for keyword in ['ajax', 'xhr']):
            return 'ajax'
        elif any(keyword in url_lower for keyword in ['auth', 'login', 'token']):
            return 'auth'
        else:
            return 'unknown'
    
    def _is_potential_api(self, request: Dict[str, Any]) -> bool:
        """Check if request is a potential API endpoint"""
        url = request.get('url', '').lower()
        content_type = request.get('headers', {}).get('Content-Type', '').lower()
        
        # URL-based detection
        api_indicators = [
            '/api/', '/rest/', '/graphql', '/ajax/',
            '.json', '.xml', 'endpoint', 'service'
        ]
        
        if any(indicator in url for indicator in api_indicators):
            return True
        
        # Content-type based detection
        api_content_types = [
            'application/json', 'application/xml', 'text/xml',
            'application/soap+xml'
        ]
        
        if any(ct in content_type for ct in api_content_types):
            return True
        
        # Method-based (non-GET requests are more likely to be APIs)
        if request.get('method', 'GET') != 'GET':
            return True
        
        return False
    
    def normalize_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize request format
        
        Args:
            request: Input request
            
        Returns:
            dict: Normalized request
        """
        normalized = {
            'method': request.get('method', 'GET').upper(),
            'url': request.get('url', ''),
            'headers': request.get('headers', {}).copy(),
            'data': request.get('data'),
            'cookies': request.get('cookies', {}).copy()
        }
        
        # Ensure common headers
        if 'User-Agent' not in normalized['headers']:
            normalized['headers']['User-Agent'] = 'Mozilla/5.0 (compatible; API-Tester/1.0)'
        
        if 'Accept' not in normalized['headers']:
            normalized['headers']['Accept'] = '*/*'
        
        return normalized
    
    def generate_curl(self, request: Dict[str, Any]) -> str:
        """
        Generate cURL command from request
        
        Args:
            request: Request data
            
        Returns:
            str: cURL command
        """
        parts = ['curl']
        
        # Method
        if request.get('method') and request['method'].upper() != 'GET':
            parts.append(f"-X {request['method'].upper()}")
        
        # URL
        parts.append(f'"{request.get("url", "")}"')
        
        # Headers
        for key, value in request.get('headers', {}).items():
            parts.append(f'-H "{key}: {value}"')
        
        # Data
        if request.get('data'):
            parts.append(f'-d "{request["data"]}"')
        
        # Cookies
        if request.get('cookies'):
            cookie_str = '; '.join([f'{k}={v}' for k, v in request['cookies'].items()])
            parts.append(f'-b "{cookie_str}"')
        
        return ' '.join(parts)
