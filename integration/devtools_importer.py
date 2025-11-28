"""
DevTools Importer - Import and process browser DevTools data
"""

import re
import json
import logging
import base64
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class DevToolsImporter:
    """Import and process browser DevTools data"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def import_from_clipboard(self) -> Optional[str]:
        """
        Import DevTools data from clipboard
        
        Returns:
            str: DevTools data or None
        """
        try:
            import pyperclip
            data = pyperclip.paste()
            
            if data and self._looks_like_devtools_data(data):
                logger.info("DevTools data imported from clipboard")
                return data
            else:
                logger.warning("Clipboard data doesn't look like DevTools output")
                return None
                
        except ImportError:
            logger.warning("pyperclip not available for clipboard access")
            return None
        except Exception as e:
            logger.error(f"Error importing from clipboard: {e}")
            return None
    
    def import_from_file(self, file_path: str) -> Optional[str]:
        """
        Import DevTools data from file
        
        Args:
            file_path: Path to file
            
        Returns:
            str: DevTools data or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            if self._looks_like_devtools_data(data):
                logger.info(f"DevTools data imported from file: {file_path}")
                return data
            else:
                logger.warning(f"File content doesn't look like DevTools data: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error importing from file {file_path}: {e}")
            return None
    
    def parse_network_data(self, devtools_data: str) -> List[Dict[str, Any]]:
        """
        Parse DevTools network data
        
        Args:
            devtools_data: Raw DevTools data
            
        Returns:
            list: Parsed network requests
        """
        requests = []
        
        try:
            # Try different parsing methods
            parsing_methods = [
                self._parse_json_har,
                self._parse_text_logs,
                self._parse_curl_commands,
                self._parse_raw_requests
            ]
            
            for method in parsing_methods:
                parsed = method(devtools_data)
                if parsed:
                    requests.extend(parsed)
                    break
            
            # Remove duplicates
            unique_requests = self._remove_duplicate_requests(requests)
            
            logger.info(f"Parsed {len(unique_requests)} unique requests from DevTools data")
            return unique_requests
            
        except Exception as e:
            logger.error(f"Error parsing DevTools network data: {e}")
            return []
    
    def _parse_json_har(self, data: str) -> List[Dict[str, Any]]:
        """Parse HAR (HTTP Archive) JSON format"""
        try:
            har_data = json.loads(data)
            requests = []
            
            # Extract from HAR entries
            entries = har_data.get('log', {}).get('entries', [])
            
            for entry in entries:
                request = entry.get('request', {})
                response = entry.get('response', {})
                
                parsed_request = {
                    'url': request.get('url', ''),
                    'method': request.get('method', 'GET'),
                    'headers': {},
                    'post_data': request.get('postData'),
                    'response_status': response.get('status'),
                    'response_size': response.get('content', {}).get('size', 0),
                    'source': 'har'
                }
                
                # Parse headers
                for header in request.get('headers', []):
                    parsed_request['headers'][header['name']] = header['value']
                
                requests.append(parsed_request)
            
            return requests
            
        except json.JSONDecodeError:
            return []
        except Exception as e:
            logger.debug(f"Error parsing HAR JSON: {e}")
            return []
    
    def _parse_text_logs(self, data: str) -> List[Dict[str, Any]]:
        """Parse text-based network logs"""
        requests = []
        lines = data.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for URL patterns
            url_patterns = [
                r'https?://[^\s<>"{}|\\^`\[\]]+',
                r'\"url\"\s*:\s*\"([^\"]+)\"',
                r'GET\s+([^\s]+)',
                r'POST\s+([^\s]+)',
                r'PUT\s+([^\s]+)',
                r'DELETE\s+([^\s]+)'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, line)
                for url in matches:
                    if self._is_valid_url(url):
                        request = {
                            'url': url,
                            'method': self._detect_http_method(line),
                            'headers': self._extract_headers_from_text(line),
                            'source': 'text_logs'
                        }
                        requests.append(request)
        
        return requests
    
    def _parse_curl_commands(self, data: str) -> List[Dict[str, Any]]:
        """Parse cURL commands"""
        requests = []
        
        # Find cURL commands
        curl_pattern = r'curl\s+[^\']*\'([^\']+)\'[^\']*'
        matches = re.finditer(curl_pattern, data, re.IGNORECASE)
        
        for match in matches:
            curl_command = match.group(0)
            
            # Extract URL
            url_match = re.search(r"curl\s+['\"]([^'\"]+)['\"]", curl_command)
            if not url_match:
                url_match = re.search(r'curl\s+([^\s]+)', curl_command)
            
            if url_match:
                request = {
                    'url': url_match.group(1),
                    'method': self._extract_curl_method(curl_command),
                    'headers': self._extract_curl_headers(curl_command),
                    'source': 'curl'
                }
                requests.append(request)
        
        return requests
    
    def _parse_raw_requests(self, data: str) -> List[Dict[str, Any]]:
        """Parse raw HTTP requests"""
        requests = []
        
        # Look for HTTP request blocks
        request_blocks = re.findall(r'(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+[^\n]+\n(?:\s*[^:\s]+:\s*[^\n]+\n)*\s*\n?', data)
        
        for block in request_blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            # Parse request line
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) >= 2:
                request = {
                    'method': parts[0],
                    'url': parts[1] if parts[1].startswith('http') else f"https://example.com{parts[1]}",
                    'headers': {},
                    'source': 'raw_http'
                }
                
                # Parse headers
                for line in lines[1:]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        request['headers'][key.strip()] = value.strip()
                
                requests.append(request)
        
        return requests
    
    def _looks_like_devtools_data(self, data: str) -> bool:
        """Check if data looks like DevTools output"""
        if not data or len(data.strip()) < 10:
            return False
        
        # Check for common DevTools patterns
        devtools_indicators = [
            'HTTP/', 'GET ', 'POST ', 'https://', 'http://',
            'Content-Type', 'User-Agent', 'curl', '{"log":',
            '"entries":', '"request":', '"response":'
        ]
        
        data_lower = data.lower()
        indicators_found = sum(1 for indicator in devtools_indicators if indicator.lower() in data_lower)
        
        return indicators_found >= 2
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _detect_http_method(self, text: str) -> str:
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
        elif 'HEAD' in text_upper:
            return 'HEAD'
        elif 'OPTIONS' in text_upper:
            return 'OPTIONS'
        else:
            return 'GET'
    
    def _extract_headers_from_text(self, text: str) -> Dict[str, str]:
        """Extract headers from text"""
        headers = {}
        
        # Look for header patterns
        header_pattern = r'([^:\s]+)\s*:\s*([^\n]+)'
        matches = re.finditer(header_pattern, text)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            headers[key] = value
        
        return headers
    
    def _extract_curl_method(self, curl_command: str) -> str:
        """Extract HTTP method from cURL command"""
        if '-X' in curl_command or '--request' in curl_command:
            method_match = re.search(r'-(?:X|-\w*request)\s+(\w+)', curl_command)
            if method_match:
                return method_match.group(1).upper()
        return 'GET'
    
    def _extract_curl_headers(self, curl_command: str) -> Dict[str, str]:
        """Extract headers from cURL command"""
        headers = {}
        
        header_matches = re.findall(r"-(?:H|-\w*header)\s+['\"]([^'\"]+)['\"]", curl_command)
        for header in header_matches:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return headers
    
    def _remove_duplicate_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate requests based on URL and method"""
        seen = set()
        unique_requests = []
        
        for request in requests:
            key = (request['url'], request['method'])
            if key not in seen:
                seen.add(key)
                unique_requests.append(request)
        
        return unique_requests
    
    def analyze_imported_data(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze imported DevTools data
        
        Args:
            requests: List of parsed requests
            
        Returns:
            dict: Analysis results
        """
        analysis = {
            'total_requests': len(requests),
            'methods': {},
            'domains': {},
            'content_types': {},
            'potential_apis': 0,
            'auth_requests': 0
        }
        
        for request in requests:
            # Count methods
            method = request.get('method', 'GET')
            analysis['methods'][method] = analysis['methods'].get(method, 0) + 1
            
            # Count domains
            try:
                domain = urlparse(request['url']).netloc
                analysis['domains'][domain] = analysis['domains'].get(domain, 0) + 1
            except:
                pass
            
            # Check content types
            headers = request.get('headers', {})
            content_type = headers.get('Content-Type', '')
            if content_type:
                analysis['content_types'][content_type] = analysis['content_types'].get(content_type, 0) + 1
            
            # Check for potential APIs
            if self._is_potential_api_request(request):
                analysis['potential_apis'] += 1
            
            # Check for authentication
            if any(key.lower() == 'authorization' for key in headers.keys()):
                analysis['auth_requests'] += 1
        
        return analysis
    
    def _is_potential_api_request(self, request: Dict[str, Any]) -> bool:
        """Check if request is a potential API endpoint"""
        url = request.get('url', '').lower()
        content_type = request.get('headers', {}).get('Content-Type', '').lower()
        
        # URL-based detection
        api_indicators = [
            '/api/', '/rest/', '/graphql', '/ajax/',
            '.json', '.xml', 'endpoint', 'service',
            'v1/', 'v2/', 'v3/'
        ]
        
        if any(indicator in url for indicator in api_indicators):
            return True
        
        # Content-type based detection
        api_content_types = [
            'application/json', 'application/xml', 'text/xml',
            'application/soap+xml', 'application/javascript'
        ]
        
        if any(ct in content_type for ct in api_content_types):
            return True
        
        return False
    
    def export_parsed_requests(self, requests: List[Dict[str, Any]], 
                              format: str = 'json') -> str:
        """
        Export parsed requests in specified format
        
        Args:
            requests: List of parsed requests
            format: Export format (json, text, curl)
            
        Returns:
            str: Exported data
        """
        if format == 'json':
            return json.dumps(requests, indent=2, ensure_ascii=False)
        elif format == 'text':
            return self._export_as_text(requests)
        elif format == 'curl':
            return self._export_as_curl(requests)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_as_text(self, requests: List[Dict[str, Any]]) -> str:
        """Export requests as text"""
        lines = []
        
        for i, request in enumerate(requests, 1):
            lines.append(f"Request {i}:")
            lines.append(f"  URL: {request.get('url', 'N/A')}")
            lines.append(f"  Method: {request.get('method', 'GET')}")
            lines.append(f"  Source: {request.get('source', 'unknown')}")
            
            headers = request.get('headers', {})
            if headers:
                lines.append("  Headers:")
                for key, value in headers.items():
                    lines.append(f"    {key}: {value}")
            
            lines.append("")  # Empty line between requests
        
        return '\n'.join(lines)
    
    def _export_as_curl(self, requests: List[Dict[str, Any]]) -> str:
        """Export requests as cURL commands"""
        curl_commands = []
        
        for request in requests:
            parts = ['curl']
            
            # Method
            method = request.get('method', 'GET')
            if method != 'GET':
                parts.append(f"-X {method}")
            
            # URL
            parts.append(f'"{request.get("url", "")}"')
            
            # Headers
            headers = request.get('headers', {})
            for key, value in headers.items():
                parts.append(f'-H "{key}: {value}"')
            
            curl_commands.append(' '.join(parts))
        
        return '\n\n'.join(curl_commands)
