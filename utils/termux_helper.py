"""
Termux Helper - Utilities for Termux environment
"""

import os
import sys
import logging
import subprocess
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TermuxHelper:
    """Helper class for Termux-specific functionality"""
    
    def __init__(self):
        self.is_termux = self._check_termux_environment()
        self.x11_available = False
        self.termux_packages = []
        
        if self.is_termux:
            self._initialize_termux()
    
    def _check_termux_environment(self) -> bool:
        """Check if running in Termux environment"""
        try:
            # Check for Termux specific paths and environment variables
            termux_indicators = [
                '/data/data/com.termux/files/usr',
                'TERMUX_VERSION',
                'PREFIX',
            ]
            
            for indicator in termux_indicators:
                if indicator in os.environ or os.path.exists(indicator):
                    return True
            
            # Check if running on Android
            if hasattr(os, 'uname'):
                uname = os.uname()
                if 'android' in uname.sysname.lower() or 'android' in uname.version.lower():
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking Termux environment: {e}")
            return False
    
    def _initialize_termux(self):
        """Initialize Termux-specific settings"""
        try:
            # Check X11 availability
            self.x11_available = self.check_x11_availability()
            
            # Get installed packages
            self.termux_packages = self.get_installed_packages()
            
            logger.info("Termux environment initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Termux: {e}")
    
    def is_termux_environment(self) -> bool:
        """Check if running in Termux"""
        return self.is_termux
    
    def check_x11_availability(self) -> bool:
        """Check if Termux-X11 is available"""
        if not self.is_termux:
            return False
        
        try:
            # Check if X11 packages are installed
            x11_packages = ['termux-x11', 'x11-repo']
            installed = self.get_installed_packages()
            
            for pkg in x11_packages:
                if pkg in installed:
                    return True
            
            # Check if DISPLAY environment variable is set
            if os.environ.get('DISPLAY'):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking X11 availability: {e}")
            return False
    
    def get_installed_packages(self) -> List[str]:
        """Get list of installed Termux packages"""
        if not self.is_termux:
            return []
        
        try:
            result = subprocess.run(
                ['pkg', 'list-installed'],
                capture_output=True, text=True, check=True
            )
            
            packages = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Extract package name (first word)
                    pkg_name = line.split()[0]
                    packages.append(pkg_name)
            
            return packages
            
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return []
    
    def install_package(self, package_name: str) -> bool:
        """
        Install a Termux package
        
        Args:
            package_name: Name of package to install
            
        Returns:
            bool: True if successful
        """
        if not self.is_termux:
            logger.warning("Not in Termux environment, cannot install packages")
            return False
        
        try:
            logger.info(f"Installing package: {package_name}")
            
            result = subprocess.run(
                ['pkg', 'install', '-y', package_name],
                capture_output=True, text=True, check=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {package_name}")
                # Update installed packages list
                self.termux_packages = self.get_installed_packages()
                return True
            else:
                logger.error(f"Failed to install {package_name}: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing package {package_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing package: {e}")
            return False
    
    def install_x11_packages(self) -> bool:
        """Install Termux-X11 related packages"""
        if not self.is_termux:
            return False
        
        try:
            # Install X11 repository
            x11_repo_installed = self.install_package('x11-repo')
            if not x11_repo_installed:
                return False
            
            # Install Termux-X11
            termux_x11_installed = self.install_package('termux-x11')
            if not termux_x11_installed:
                return False
            
            # Update X11 availability
            self.x11_available = self.check_x11_availability()
            
            return self.x11_available
            
        except Exception as e:
            logger.error(f"Error installing X11 packages: {e}")
            return False
    
    def install_browser(self, browser: str) -> bool:
        """
        Install a browser in Termux
        
        Args:
            browser: Browser name (firefox, chromium)
            
        Returns:
            bool: True if successful
        """
        if not self.is_termux:
            return False
        
        browser_packages = {
            'firefox': 'firefox',
            'chromium': 'chromium'
        }
        
        if browser not in browser_packages:
            logger.error(f"Unsupported browser: {browser}")
            return False
        
        package_name = browser_packages[browser]
        return self.install_package(package_name)
    
    def setup_termux_environment(self) -> Dict[str, bool]:
        """
        Setup complete Termux environment
        
        Returns:
            dict: Setup results
        """
        if not self.is_termux:
            return {'success': False, 'reason': 'not_termux'}
        
        results = {
            'x11_setup': False,
            'browsers_installed': [],
            'python_packages': False
        }
        
        try:
            # Update packages
            logger.info("Updating Termux packages...")
            subprocess.run(['pkg', 'update', '-y'], check=True)
            subprocess.run(['pkg', 'upgrade', '-y'], check=True)
            
            # Install X11 if not available
            if not self.x11_available:
                results['x11_setup'] = self.install_x11_packages()
            else:
                results['x11_setup'] = True
            
            # Install browsers
            browsers = ['firefox', 'chromium']
            for browser in browsers:
                if self.install_browser(browser):
                    results['browsers_installed'].append(browser)
            
            # Install Python development packages
            dev_packages = ['python', 'python-pip', 'git', 'vim']
            for pkg in dev_packages:
                self.install_package(pkg)
            
            results['python_packages'] = True
            results['success'] = True
            
            logger.info("Termux environment setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Termux environment: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def get_system_info(self) -> Dict[str, str]:
        """Get Termux system information"""
        if not self.is_termux:
            return {'environment': 'not_termux'}
        
        info = {
            'environment': 'termux',
            'x11_available': str(self.x11_available),
            'installed_packages_count': str(len(self.termux_packages))
        }
        
        try:
            # Get Android version
            if os.path.exists('/system/build.prop'):
                with open('/system/build.prop', 'r') as f:
                    for line in f:
                        if line.startswith('ro.build.version.release='):
                            info['android_version'] = line.split('=')[1].strip()
                            break
            
            # Get architecture
            if hasattr(os, 'uname'):
                uname = os.uname()
                info['architecture'] = uname.machine
                info['system'] = uname.sysname
                info['version'] = uname.version
            
            # Get storage information
            storage_cmd = subprocess.run(
                ['df', '-h', '/data'],
                capture_output=True, text=True
            )
            if storage_cmd.returncode == 0:
                lines = storage_cmd.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        info['storage_used'] = parts[2]
                        info['storage_available'] = parts[3]
                        info['storage_percent'] = parts[4]
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
        
        return info
    
    def run_x11_application(self, command: List[str], 
                           display: str = ":0") -> Optional[subprocess.Popen]:
        """
        Run an X11 application in Termux
        
        Args:
            command: Command to run
            display: X11 display
            
        Returns:
            subprocess.Popen: Process object or None if failed
        """
        if not self.is_termux or not self.x11_available:
            logger.error("X11 not available in Termux")
            return None
        
        try:
            # Set display
            env = os.environ.copy()
            env['DISPLAY'] = display
            
            # Start the application
            process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Started X11 application: {' '.join(command)}")
            return process
            
        except Exception as e:
            logger.error(f"Error running X11 application: {e}")
            return None
    
    def check_storage_permission(self) -> bool:
        """Check if Termux has storage permission"""
        if not self.is_termux:
            return True
        
        try:
            # Try to create a file in storage
            test_file = '/sdcard/termux_test.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except:
            return False
    
    def request_storage_permission(self) -> bool:
        """Request storage permission in Termux"""
        if not self.is_termux:
            return True
        
        try:
            # Use termux-setup-storage to request permission
            result = subprocess.run(
                ['termux-setup-storage'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info("Storage permission granted")
                return True
            else:
                logger.error("Failed to get storage permission")
                return False
                
        except Exception as e:
            logger.error(f"Error requesting storage permission: {e}")
            return False
    
    def get_termux_api_capabilities(self) -> List[str]:
        """Get available Termux API capabilities"""
        if not self.is_termux:
            return []
        
        capabilities = []
        api_commands = [
            'termux-battery-status',
            'termux-brightness',
            'termux-camera-info',
            'termux-clipboard-get',
            'termux-clipboard-set',
            'termux-contact-list',
            'termux-download',
            'termux-location',
            'termux-notification',
            'termux-share',
            'termux-telephony-call',
            'termux-toast',
            'termux-vibrate',
            'termux-volume'
        ]
        
        for cmd in api_commands:
            try:
                result = subprocess.run(
                    ['which', cmd],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    capabilities.append(cmd)
            except:
                pass
        
        return capabilities
