"""
Browser Launcher - Launch and manage browsers in different environments
"""

import os
import logging
import subprocess
import threading
import time
from typing import Optional, Dict, Any, List
import webbrowser

logger = logging.getLogger(__name__)

class BrowserLauncher:
    """Launch and manage browsers for API testing"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.browser_processes = {}
        self.browser_status = {}
        
        # Browser paths configuration
        self.browser_paths = {
            'firefox': self.config.get('browser', {}).get('firefox_path', 'firefox'),
            'chromium': self.config.get('browser', {}).get('chromium_path', 'chromium-browser'),
            'chrome': self.config.get('browser', {}).get('chrome_path', 'google-chrome')
        }
    
    def launch_firefox(self, url: str = None, headless: bool = False) -> bool:
        """
        Launch Firefox browser
        
        Args:
            url: URL to open
            headless: Run in headless mode
            
        Returns:
            bool: True if successful
        """
        try:
            firefox_path = self.browser_paths['firefox']
            
            # Build command
            cmd = [firefox_path]
            
            if headless:
                cmd.append('--headless')
            
            if url:
                cmd.append(url)
            
            # Launch browser
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process info
            self.browser_processes['firefox'] = process
            self.browser_status['firefox'] = {
                'running': True,
                'pid': process.pid,
                'start_time': time.time(),
                'headless': headless
            }
            
            logger.info(f"Firefox launched (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Error launching Firefox: {e}")
            return False
    
    def launch_chromium(self, url: str = None, headless: bool = False) -> bool:
        """
        Launch Chromium browser
        
        Args:
            url: URL to open
            headless: Run in headless mode
            
        Returns:
            bool: True if successful
        """
        try:
            chromium_path = self.browser_paths['chromium']
            
            # Build command
            cmd = [chromium_path]
            
            if headless:
                cmd.extend(['--headless', '--disable-gpu'])
            
            # Add common flags
            cmd.extend([
                '--no-first-run',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows'
            ])
            
            if url:
                cmd.append(url)
            
            # Launch browser
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process info
            self.browser_processes['chromium'] = process
            self.browser_status['chromium'] = {
                'running': True,
                'pid': process.pid,
                'start_time': time.time(),
                'headless': headless
            }
            
            logger.info(f"Chromium launched (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Error launching Chromium: {e}")
            return False
    
    def launch_chrome(self, url: str = None, headless: bool = False) -> bool:
        """
        Launch Google Chrome browser
        
        Args:
            url: URL to open
            headless: Run in headless mode
            
        Returns:
            bool: True if successful
        """
        try:
            chrome_path = self.browser_paths['chrome']
            
            # Build command
            cmd = [chrome_path]
            
            if headless:
                cmd.extend(['--headless', '--disable-gpu'])
            
            # Add common flags
            cmd.extend([
                '--no-first-run',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows'
            ])
            
            if url:
                cmd.append(url)
            
            # Launch browser
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process info
            self.browser_processes['chrome'] = process
            self.browser_status['chrome'] = {
                'running': True,
                'pid': process.pid,
                'start_time': time.time(),
                'headless': headless
            }
            
            logger.info(f"Chrome launched (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Error launching Chrome: {e}")
            return False
    
    def launch_browser_choice(self, browser: str = None, **kwargs) -> bool:
        """
        Launch browser based on choice or auto-detection
        
        Args:
            browser: Browser name (firefox, chromium, chrome)
            **kwargs: Additional arguments
            
        Returns:
            bool: True if successful
        """
        if not browser:
            # Auto-detect available browser
            browser = self.detect_available_browser()
        
        if browser == 'firefox':
            return self.launch_firefox(**kwargs)
        elif browser == 'chromium':
            return self.launch_chromium(**kwargs)
        elif browser == 'chrome':
            return self.launch_chrome(**kwargs)
        else:
            logger.error(f"Unsupported browser: {browser}")
            return False
    
    def detect_available_browser(self) -> str:
        """
        Detect available browser on the system
        
        Returns:
            str: Browser name or 'unknown'
        """
        browsers = ['firefox', 'chromium', 'chrome']
        
        for browser in browsers:
            path = self.browser_paths[browser]
            try:
                # Check if browser executable exists
                if os.path.exists(path):
                    logger.info(f"Detected browser: {browser} at {path}")
                    return browser
                
                # Check if browser is in PATH
                result = subprocess.run(
                    ['which', path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"Detected browser in PATH: {browser}")
                    return browser
                    
            except Exception as e:
                logger.debug(f"Error checking browser {browser}: {e}")
        
        logger.warning("No supported browser detected")
        return 'unknown'
    
    def stop_browser(self, browser: str = None) -> bool:
        """
        Stop browser process
        
        Args:
            browser: Browser name (if None, stop all)
            
        Returns:
            bool: True if successful
        """
        try:
            if browser:
                browsers_to_stop = [browser]
            else:
                browsers_to_stop = list(self.browser_processes.keys())
            
            success = True
            for browser_name in browsers_to_stop:
                if browser_name in self.browser_processes:
                    process = self.browser_processes[browser_name]
                    if process.poll() is None:  # Still running
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                            logger.info(f"Browser {browser_name} stopped")
                        except subprocess.TimeoutExpired:
                            process.kill()
                            logger.warning(f"Browser {browser_name} force killed")
                    
                    # Update status
                    self.browser_status[browser_name]['running'] = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
            return False
    
    def is_browser_running(self, browser: str) -> bool:
        """
        Check if browser is running
        
        Args:
            browser: Browser name
            
        Returns:
            bool: True if running
        """
        if browser not in self.browser_processes:
            return False
        
        process = self.browser_processes[browser]
        return process.poll() is None
    
    def get_browser_status(self, browser: str = None) -> Dict[str, Any]:
        """
        Get browser status information
        
        Args:
            browser: Browser name (if None, get all)
            
        Returns:
            dict: Status information
        """
        if browser:
            return self.browser_status.get(browser, {})
        else:
            return self.browser_status.copy()
    
    def open_url(self, url: str, browser: str = None) -> bool:
        """
        Open URL in browser
        
        Args:
            url: URL to open
            browser: Browser name
            
        Returns:
            bool: True if successful
        """
        try:
            if browser:
                # Use specific browser
                if browser == 'firefox':
                    return self.launch_firefox(url=url)
                elif browser == 'chromium':
                    return self.launch_chromium(url=url)
                elif browser == 'chrome':
                    return self.launch_chrome(url=url)
                else:
                    logger.error(f"Unsupported browser: {browser}")
                    return False
            else:
                # Use system default browser
                webbrowser.open(url)
                logger.info(f"Opened URL in default browser: {url}")
                return True
                
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            return False
    
    def get_browser_info(self) -> Dict[str, Any]:
        """
        Get detailed browser information
        
        Returns:
            dict: Browser information
        """
        info = {
            'available_browsers': [],
            'default_browser': webbrowser.get().name if webbrowser.get() else 'unknown',
            'termux_environment': self._is_termux_environment()
        }
        
        # Check available browsers
        browsers = ['firefox', 'chromium', 'chrome']
        for browser in browsers:
            path = self.browser_paths[browser]
            if self._check_browser_available(browser):
                info['available_browsers'].append({
                    'name': browser,
                    'path': path,
                    'available': True
                })
            else:
                info['available_browsers'].append({
                    'name': browser,
                    'path': path,
                    'available': False
                })
        
        return info
    
    def _check_browser_available(self, browser: str) -> bool:
        """Check if browser is available"""
        path = self.browser_paths[browser]
        
        # Check if file exists
        if os.path.exists(path):
            return True
        
        # Check if in PATH
        try:
            result = subprocess.run(
                ['which', path],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _is_termux_environment(self) -> bool:
        """Check if running in Termux environment"""
        termux_indicators = [
            '/data/data/com.termux/files/usr',
            'TERMUX_VERSION'
        ]
        
        for indicator in termux_indicators:
            if indicator in os.environ or os.path.exists(indicator):
                return True
        return False
    
    def setup_browser_environment(self) -> Dict[str, Any]:
        """
        Setup browser environment
        
        Returns:
            dict: Setup results
        """
        results = {
            'success': True,
            'browsers_configured': [],
            'errors': []
        }
        
        try:
            # Check and configure each browser
            browsers = ['firefox', 'chromium', 'chrome']
            
            for browser in browsers:
                if self._check_browser_available(browser):
                    results['browsers_configured'].append(browser)
                else:
                    results['errors'].append(f"Browser not available: {browser}")
            
            if not results['browsers_configured']:
                results['success'] = False
                results['errors'].append("No browsers available")
            
            return results
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Setup error: {str(e)}")
            return results
