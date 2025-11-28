"""
Captcha Solver - Handle various types of captchas
"""

import re
import logging
import requests
from typing import Optional, Dict, Any
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class CaptchaSolver:
    def __init__(self, config=None):
        self.config = config or {}
        self.supported_types = ['math', 'text', 'image', 'recaptcha']
    
    def solve_captcha(self, html: str, captcha_data: Dict[str, Any] = None) -> Optional[str]:
        """
        Solve captcha from HTML or provided data
        
        Args:
            html: HTML content containing captcha
            captcha_data: Additional captcha data
            
        Returns:
            str: Captcha solution or None if unsolved
        """
        # Try to detect captcha type
        captcha_type = self._detect_captcha_type(html, captcha_data)
        
        if not captcha_type:
            logger.info("No captcha detected")
            return None
        
        logger.info(f"Detected captcha type: {captcha_type}")
        
        if captcha_type == 'math':
            return self._solve_math_captcha(html)
        elif captcha_type == 'text':
            return self._solve_text_captcha(html, captcha_data)
        elif captcha_type == 'image':
            return self._solve_image_captcha(html, captcha_data)
        elif captcha_type == 'recaptcha':
            return self._solve_recaptcha(html, captcha_data)
        else:
            logger.warning(f"Unsupported captcha type: {captcha_type}")
            return None
    
    def _detect_captcha_type(self, html: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Detect the type of captcha"""
        html_lower = html.lower()
        
        # Math captcha detection
        math_patterns = [
            r'what is \d+\s*\+\s*\d+\s*\?',
            r'\d+\s*\+\s*\d+\s*=',
            r'math question',
            r'solve.*math'
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, html_lower, re.IGNORECASE):
                return 'math'
        
        # reCAPTCHA detection
        if 'recaptcha' in html_lower or 'g-recaptcha' in html_lower:
            return 'recaptcha'
        
        # Image captcha detection
        if re.search(r'<img[^>]*src=[^>]*captcha[^>]*>', html_lower):
            return 'image'
        if 'captcha' in html_lower and 'image' in html_lower:
            return 'image'
        
        # Text captcha detection
        if re.search(r'enter.*text.*shown', html_lower):
            return 'text'
        if 'captcha' in html_lower and 'text' in html_lower:
            return 'text'
        
        # Generic captcha detection
        if 'captcha' in html_lower:
            # Check for input fields that might be captcha
            if re.search(r'<input[^>]*(captcha|security|verification)[^>]*>', html_lower):
                return 'text'
        
        return None
    
    def _solve_math_captcha(self, html: str) -> Optional[str]:
        """Solve math-based captchas"""
        math_patterns = [
            r'what is (\d+)\s*\+\s*(\d+)\s*\?',
            r'(\d+)\s*\+\s*(\d+)\s*=',
            r'captcha.*?(\d+).*?(\d+)',
            r'solve.*?(\d+).*?(\d+)'
        ]
        
        for pattern in math_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2))
                    result = num1 + num2
                    logger.info(f"Solved math captcha: {num1} + {num2} = {result}")
                    return str(result)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _solve_text_captcha(self, html: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve text-based captchas"""
        # For text captchas, we might need external services
        # This is a basic implementation
        logger.info("Text captcha detected - manual solution required")
        return None
    
    def _solve_image_captcha(self, html: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve image-based captchas"""
        # Extract image URL
        img_pattern = r'<img[^>]*src=[\'"]([^\'"]*captcha[^\'"]*)[\'"][^>]*>'
        match = re.search(img_pattern, html, re.IGNORECASE)
        
        if not match:
            return None
        
        img_url = match.group(1)
        if not img_url.startswith(('http://', 'https://')):
            # Handle relative URLs
            base_url = captcha_data.get('base_url', '') if captcha_data else ''
            if base_url:
                from urllib.parse import urljoin
                img_url = urljoin(base_url, img_url)
            else:
                logger.warning("Cannot resolve relative image URL without base_url")
                return None
        
        try:
            # Download captcha image
            response = requests.get(img_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to download captcha image: {response.status_code}")
                return None
            
            # For now, we'll just log that we found an image captcha
            # In a real implementation, you would use OCR here
            logger.info(f"Image captcha found at {img_url} - OCR solution not implemented")
            
            # Example of how you might implement OCR:
            # from pytesseract import image_to_string
            # image = Image.open(io.BytesIO(response.content))
            # solution = image_to_string(image).strip()
            # return solution
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing image captcha: {e}")
            return None
    
    def _solve_recaptcha(self, html: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve reCAPTCHA challenges"""
        logger.info("reCAPTCHA detected - external service required")
        
        # reCAPTCHA requires external services like 2captcha, anti-captcha, etc.
        # This is a placeholder for integration with such services
        
        site_key_pattern = r'data-sitekey=[\'"]([^\'"]+)[\'"]'
        match = re.search(site_key_pattern, html)
        
        if match:
            site_key = match.group(1)
            logger.info(f"reCAPTCHA site key: {site_key}")
            
            # Here you would integrate with a captcha solving service
            # Example:
            # if self.config.get('captcha_service'):
            #     return self._use_captcha_service(site_key, captcha_data)
        
        return None
    
    def _use_captcha_service(self, site_key: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Use external captcha solving service"""
        # Placeholder for captcha service integration
        service = self.config.get('captcha_service')
        
        if service == '2captcha':
            return self._solve_with_2captcha(site_key, captcha_data)
        elif service == 'anti_captcha':
            return self._solve_with_anti_captcha(site_key, captcha_data)
        else:
            logger.warning(f"Unknown captcha service: {service}")
            return None
    
    def _solve_with_2captcha(self, site_key: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve using 2captcha service"""
        # Implementation for 2captcha API
        logger.info("2captcha integration not implemented")
        return None
    
    def _solve_with_anti_captcha(self, site_key: str, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve using anti-captcha service"""
        # Implementation for anti-captcha API
        logger.info("Anti-captcha integration not implemented")
        return None
    
    def can_solve_automatically(self, html: str) -> bool:
        """Check if captcha can be solved automatically"""
        captcha_type = self._detect_captcha_type(html, None)
        
        if captcha_type == 'math':
            return True
        elif captcha_type in ['text', 'image']:
            # These might be solvable with external services
            return self.config.get('captcha_service') is not None
        else:
            return False
