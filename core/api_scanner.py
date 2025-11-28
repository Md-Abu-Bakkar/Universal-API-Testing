"""
API Scanner - Core functionality for API detection and testing
"""

import re
import json
import requests
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class APIScanner:
    def __init__(self, config=None):
        self.session = requests.Session()
        self.detected_apis = []
        self.config = config or {}
        
        # Common API patterns
        self.api_patterns = [
            r'https?://[^\s"\']+\.php(?:\?[^\s"\']*)?',
            r'https?://[^\s"\']+\.json(?:\?[^\s"\']*)?',
            r'https?://[^\s"\']+\.xml(?:\?[^\s"\']*)?',
            r'https?://[^\s"\']+/api/[^\s"\']+',
            r'https?://[^\s"\']+/rest/[^\s"\']+',
            r'https?://[^\s"\']+/graphql',
            r'https?://[^\s"\']+/ajax/[^\s"\']+',
            r'https?://[^\s"\']+/data/[^\s"\']+',
        ]
        
        # Headers for API requests
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Update headers from config
        if self.config.get('browser', {}).get('user_agent'):
            self.default_headers['User-Agent'] = self.config['browser']['user_agent']
    
    def extract_apis(self, devtools_data: str) -> List[Dict[str, Any]]:
        """
        Extract API endpoints from DevTools raw data
        
        Args:
            devtools_data: Raw text from browser DevTools
            
        Returns:
            List of detected APIs with metadata
        """
        logger.info("Extracting APIs from DevTools data")
        
        apis = []
        
        # Extract URLs using patterns
        for pattern in self.api_patterns:
            matches = re.finditer(pattern, devtools_data, re.IGNORECASE)
            for match in matches:
                url = match.group()
                if self._is_valid_api_url(url):
                    api_info = self._analyze_api_url(url)
                    if api_info:
                        apis.append(api_info)
        
        # Extract from JSON structures
        json_apis = self._extract_from_json(devtools_data)
        apis.extend(json_apis)
        
        # Extract from cURL commands
        curl_apis = self._extract_from_curl(devtools_data)
        apis.extend(curl_apis)
        
        # Remove duplicates
        unique_apis = self._remove_duplicate_apis(apis)
        
        logger.info(f"Extracted {len(unique_apis)} unique APIs")
        return unique_apis
    
    def test_sequential(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Test APIs sequentially and return results
        
        Args:
            apis: List of APIs to test
            
        Returns:
            List of testing results
        """
        logger.info(f"Testing {len(apis)} APIs sequentially")
        
        results = []
        timeout = self.config.get('api_detection', {}).get('timeout', 30)
        max_apis = self.config.get('api_detection', {}).get('max_apis_per_scan', 50)
        
        # Limit number of APIs to test
        if len(apis) > max_apis:
            logger.warning(f"Limiting API testing to {max_apis} out of {len(apis)} found")
            apis = apis[:max_apis]
        
        for i, api in enumerate(apis, 1):
            logger.info(f"Testing API {i}/{len(apis)}: {api['url']}")
            
            try:
                result = self._test_single_api(api, timeout)
                results.append(result)
                
                # Add delay between requests
                if i < len(apis):
                    delay = self.config.get('advanced', {}).get('delay_between_requests', 1)
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error testing API {api['url']}: {e}")
                results.append({
                    'api': api['url'],
                    'success': False,
                    'error': str(e),
                    'type': api.get('type', 'ERROR'),
                    'response': '',
                    'status_code': 0
                })
        
        return results
    
    def _is_valid_api_url(self, url: str) -> bool:
        """Check if URL is a valid API endpoint"""
        # Skip common static files
        excluded_patterns = [
            r'\.css$', r'\.js$', r'\.png$', r'\.jpg$', r'\.gif$',
            r'\.ico$', r'\.svg$', r'fonts\.', r'googleapis\.com',
            r'gstatic\.com', r'jquery', r'bootstrap'
        ]
        
        for pattern in excluded_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Check against blacklist
        blacklist = self.config.get('advanced', {}).get('blacklist_domains', [])
        for domain in blacklist:
            if domain in url:
                return False
        
        return True
    
    def _analyze_api_url(self, url: str) -> Dict[str, Any]:
        """Analyze API URL and extract metadata"""
        try:
            parsed = urlparse(url)
            
            return {
                'url': url,
                'domain': parsed.netloc,
                'path': parsed.path,
                'params': parsed.query,
                'method': self._guess_http_method(url),
                'type': self._classify_api_type(url),
                'priority': self._calculate_priority(url),
                'headers': self._generate_headers_for_api(url)
            }
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {e}")
            return None
    
    def _guess_http_method(self, url: str) -> str:
        """Guess HTTP method based on URL patterns"""
        url_lower = url.lower()
        
        if any(word in url_lower for word in ['login', 'signin', 'submit', 'post', 'send']):
            return 'POST'
        elif any(word in url_lower for word in ['get', 'fetch', 'load', 'data', 'list']):
            return 'GET'
        elif any(word in url_lower for word in ['update', 'put', 'modify']):
            return 'PUT'
        elif any(word in url_lower for word in ['delete', 'remove']):
            return 'DELETE'
        elif 'api' in url_lower or 'rest' in url_lower:
            return 'GET'
        else:
            return 'GET'  # Default to GET
    
    def _classify_api_type(self, url: str) -> str:
        """Classify API type based on URL patterns"""
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in ['sms', 'otp', 'message', 'text']):
            return 'SMS'
        elif any(pattern in url_lower for pattern in ['login', 'auth', 'signin', 'authenticate']):
            return 'AUTH'
        elif any(pattern in url_lower for pattern in ['data', 'fetch', 'get', 'list']):
            return 'DATA'
        elif any(pattern in url_lower for pattern in ['api', 'rest']):
            return 'API'
        elif any(pattern in url_lower for pattern in ['graphql']):
            return 'GRAPHQL'
        elif any(pattern in url_lower for pattern in ['ajax']):
            return 'AJAX'
        elif any(pattern in url_lower for pattern in ['file', 'upload', 'download']):
            return 'FILE'
        else:
            return 'UNKNOWN'
    
    def _calculate_priority(self, url: str) -> int:
        """Calculate testing priority for API"""
        priority = 1
        
        url_lower = url.lower()
        
        # High priority patterns
        high_priority = ['sms', 'otp', 'message', 'data_sms', 'api', 'data']
        if any(pattern in url_lower for pattern in high_priority):
            priority = 3
        
        # Medium priority patterns
        medium_priority = ['login', 'auth', 'fetch', 'get', 'ajax']
        if any(pattern in url_lower for pattern in medium_priority):
            priority = 2
        
        return priority
    
    def _generate_headers_for_api(self, url: str) -> Dict[str, str]:
        """Generate appropriate headers for API type"""
        headers = self.default_headers.copy()
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in ['api', 'rest', 'graphql']):
            headers.update({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            })
        elif any(pattern in url_lower for pattern in ['ajax']):
            headers.update({
                'X-Requested-With': 'XMLHttpRequest'
            })
        
        return headers
    
    def _extract_from_json(self, data: str) -> List[Dict[str, Any]]:
        """Extract APIs from JSON structures"""
        apis = []
        
        # Try to find JSON objects in the data
        json_patterns = [
            r'\{[^{}]*"[^"]*"\s*:\s*"[^"]*"[^{}]*\}',
            r'\[[^\[\]]*\{[^{}]*\}[^\[\]]*\]'
        ]
        
        for pattern in json_patterns:
            matches = re.finditer(pattern, data)
            for match in matches:
                try:
                    json_data = json.loads(match.group())
                    urls = self._find_urls_in_json(json_data)
                    for url in urls:
                        if self._is_valid_api_url(url):
                            api_info = self._analyze_api_url(url)
                            if api_info:
                                apis.append(api_info)
                except json.JSONDecodeError:
                    continue
        
        return apis
    
    def _extract_from_curl(self, data: str) -> List[Dict[str, Any]]:
        """Extract APIs from cURL commands"""
        apis = []
        
        curl_pattern = r'curl\s+[^\']*\'([^\']+)\''
        matches = re.finditer(curl_pattern, data, re.IGNORECASE)
        
        for match in matches:
            url = match.group(1)
            if self._is_valid_api_url(url):
                api_info = self._analyze_api_url(url)
                if api_info:
                    apis.append(api_info)
        
        return apis
    
    def _find_urls_in_json(self, data: Any) -> List[str]:
        """Recursively find URLs in JSON data"""
        urls = []
        
        if isinstance(data, dict):
            for value in data.values():
                urls.extend(self._find_urls_in_json(value))
        elif isinstance(data, list):
            for item in data:
                urls.extend(self._find_urls_in_json(item))
        elif isinstance(data, str) and data.startswith(('http://', 'https://')):
            urls.append(data)
        
        return urls
    
    def _remove_duplicate_apis(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate APIs based on URL"""
        seen_urls = set()
        unique_apis = []
        
        for api in apis:
            if api['url'] not in seen_urls:
                seen_urls.add(api['url'])
                unique_apis.append(api)
        
        # Sort by priority
        unique_apis.sort(key=lambda x: x['priority'], reverse=True)
        
        return unique_apis
    
    def _test_single_api(self, api: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Test a single API endpoint"""
        try:
            method = api.get('method', 'GET').upper()
            headers = api.get('headers', self.default_headers)
            
            request_kwargs = {
                'headers': headers,
                'timeout': timeout,
                'verify': self.config.get('security', {}).get('verify_ssl', False),
                'allow_redirects': self.config.get('security', {}).get('allow_redirects', True)
            }
            
            if method == 'GET':
                response = self.session.get(api['url'], **request_kwargs)
            elif method == 'POST':
                response = self.session.post(api['url'], **request_kwargs)
            elif method == 'PUT':
                response = self.session.put(api['url'], **request_kwargs)
            elif method == 'DELETE':
                response = self.session.delete(api['url'], **request_kwargs)
            else:
                response = self.session.request(method, api['url'], **request_kwargs)
            
            # Analyze response
            success = self._is_successful_response(response)
            response_data = self._parse_response(response)
            
            return {
                'api': api['url'],
                'success': success,
                'status_code': response.status_code,
                'type': api['type'],
                'response': response_data,
                'headers': dict(response.headers),
                'method': method,
                'size': len(response.content)
            }
            
        except requests.RequestException as e:
            return {
                'api': api['url'],
                'success': False,
                'error': str(e),
                'type': api['type'],
                'response': '',
                'status_code': 0,
                'method': api.get('method', 'GET')
            }
    
    def _is_successful_response(self, response) -> bool:
        """Check if response indicates success"""
        if response.status_code not in [200, 201, 202]:
            return False
        
        content_type = response.headers.get('content-type', '').lower()
        
        # Check for error indicators in response
        error_indicators = ['error', 'invalid', 'unauthorized', 'forbidden', 'not found']
        response_text = response.text.lower()
        
        if any(indicator in response_text for indicator in error_indicators):
            return False
        
        # Check if response contains meaningful data
        if content_type.startswith('application/json'):
            try:
                json_data = response.json()
                # If JSON is empty or contains error field
                if not json_data or ('error' in json_data and json_data['error']):
                    return False
            except:
                pass
        
        return True
    
    def _parse_response(self, response) -> str:
        """Parse and format response data"""
        try:
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                json_data = response.json()
                return json.dumps(json_data, indent=2, ensure_ascii=False)
            elif 'text/html' in content_type:
                # Return limited HTML content
                return response.text[:500] + "..." if len(response.text) > 500 else response.text
            elif 'text/plain' in content_type:
                return response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            else:
                # For binary or other content types, return info
                return f"[{content_type}] {len(response.content)} bytes"
                
        except (ValueError, UnicodeDecodeError):
            # Return as text with length limit
            return response.text[:500] + "..." if len(response.text) > 500 else response.text
    
    def get_api_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from API testing results"""
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        type_stats = {}
        for result in results:
            api_type = result.get('type', 'UNKNOWN')
            if api_type not in type_stats:
                type_stats[api_type] = 0
            type_stats[api_type] += 1
        
        return {
            'total_apis': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'type_distribution': type_stats
        }
