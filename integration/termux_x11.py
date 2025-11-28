"""
Termux X11 Manager - Handle Termux-X11 integration
"""

import os
import logging
import subprocess
from typing import Optional, Dict, Any
import threading
import time

logger = logging.getLogger(__name__)

class TermuxX11Manager:
    """Manage Termux-X11 integration"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.x11_process = None
        self.x11_server = None
        self.is_running = False
        
    def start_x11_server(self) -> bool:
        """Start Termux-X11 server"""
        try:
            if not self._check_termux_environment():
                logger.error("Not in Termux environment")
                return False
            
            # Check if X11 packages are installed
            if not self._check_x11_packages():
                logger.error("X11 packages not installed")
                return False
            
            # Start X11 server
            logger.info("Starting Termux-X11 server...")
            self.x11_process = subprocess.Popen(
                ['termux-x11'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(2)
            
            if self.x11_process.poll() is None:
                self.is_running = True
                logger.info("Termux-X11 server started successfully")
                return True
            else:
                logger.error("Failed to start Termux-X11 server")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Termux-X11 server: {e}")
            return False
    
    def stop_x11_server(self) -> bool:
        """Stop Termux-X11 server"""
        try:
            if self.x11_process and self.x11_process.poll() is None:
                self.x11_process.terminate()
                self.x11_process.wait(timeout=5)
                self.is_running = False
                logger.info("Termux-X11 server stopped")
                return True
            return True
        except Exception as e:
            logger.error(f"Error stopping Termux-X11 server: {e}")
            return False
    
    def _check_termux_environment(self) -> bool:
        """Check if running in Termux"""
        termux_indicators = [
            '/data/data/com.termux/files/usr',
            'TERMUX_VERSION'
        ]
        
        for indicator in termux_indicators:
            if indicator in os.environ or os.path.exists(indicator):
                return True
        return False
    
    def _check_x11_packages(self) -> bool:
        """Check if X11 packages are installed"""
        try:
            result = subprocess.run(
                ['pkg', 'list-installed'], 
                capture_output=True, text=True, check=True
            )
            
            required_packages = ['termux-x11', 'x11-repo']
            installed_packages = result.stdout.lower()
            
            for pkg in required_packages:
                if pkg not in installed_packages:
                    logger.warning(f"X11 package not installed: {pkg}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking X11 packages: {e}")
            return False
    
    def get_x11_status(self) -> Dict[str, Any]:
        """Get X11 server status"""
        return {
            'running': self.is_running,
            'display': os.environ.get('DISPLAY', ':0'),
            'termux_environment': self._check_termux_environment(),
            'x11_packages_installed': self._check_x11_packages()
        }
