#!/usr/bin/env python3
"""
Termux Desktop Launcher for Universal API Tester
Special script to launch the application in Termux-X11 environment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TermuxDesktopLauncher:
    def __init__(self):
        self.termux_x11_available = False
        self.x11_server_pid = None
        
    def check_termux_environment(self):
        """Check if running in Termux environment"""
        termux_indicators = [
            '/data/data/com.termux/files/usr',
            'TERMUX_VERSION'
        ]
        
        for indicator in termux_indicators:
            if indicator in os.environ or os.path.exists(indicator):
                return True
        return False
    
    def check_x11_availability(self):
        """Check if Termux-X11 is available"""
        try:
            # Check if X11 packages are installed
            result = subprocess.run(
                ['pkg', 'list-installed'], 
                capture_output=True, text=True
            )
            
            if 'termux-x11' in result.stdout:
                self.termux_x11_available = True
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking X11 availability: {e}")
            return False
    
    def start_x11_server(self):
        """Start Termux-X11 server"""
        try:
            logger.info("Starting Termux-X11 server...")
            
            # Start X11 server in background
            process = subprocess.Popen(
                ['termux-x11'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.x11_server_pid = process.pid
            logger.info(f"Termux-X11 server started with PID: {process.pid}")
            
            # Wait a moment for server to initialize
            import time
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Termux-X11 server: {e}")
            return False
    
    def stop_x11_server(self):
        """Stop Termux-X11 server"""
        if self.x11_server_pid:
            try:
                subprocess.run(['kill', str(self.x11_server_pid)])
                logger.info("Termux-X11 server stopped")
            except Exception as e:
                logger.error(f"Error stopping X11 server: {e}")
    
    def setup_display_environment(self):
        """Setup display environment variables"""
        # Set display
        os.environ['DISPLAY'] = ':0'
        
        # Set other X11 variables
        os.environ['XDG_RUNTIME_DIR'] = '/data/data/com.termux/files/usr/var/run'
        os.environ['PULSE_RUNTIME_PATH'] = '/data/data/com.termux/files/usr/var/run/pulse'
        
        logger.info("Display environment setup completed")
    
    def launch_desktop_environment(self):
        """Launch lightweight desktop environment"""
        try:
            # Launch XFCE4 (lightweight desktop)
            desktop_process = subprocess.Popen(
                ['xfce4-session'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("XFCE4 desktop environment started")
            return desktop_process
            
        except Exception as e:
            logger.error(f"Failed to launch desktop environment: {e}")
            return None
    
    def launch_api_tester_gui(self):
        """Launch API Tester in GUI mode"""
        try:
            # Add current directory to Python path
            current_dir = Path(__file__).parent
            sys.path.insert(0, str(current_dir))
            
            # Import and launch the dashboard
            from gui.dashboard import Dashboard
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            dashboard = Dashboard()
            dashboard.show()
            
            logger.info("Universal API Tester GUI launched successfully")
            return app.exec_()
            
        except ImportError as e:
            logger.error(f"GUI dependencies not available: {e}")
            return self.launch_fallback_mode()
        except Exception as e:
            logger.error(f"Error launching API Tester GUI: {e}")
            return self.launch_fallback_mode()
    
    def launch_fallback_mode(self):
        """Launch fallback mode if GUI fails"""
        try:
            from main import UniversalAPITester
            tester = UniversalAPITester()
            return tester.run_cli_mode(None)
        except Exception as e:
            logger.error(f"Fallback mode also failed: {e}")
            return 1
    
    def show_termux_instructions(self):
        """Show Termux-specific instructions"""
        print("\n" + "="*50)
        print("🚀 Universal API Tester - Termux Setup")
        print("="*50)
        print("\n📋 Before running in GUI mode:")
        print("1. Make sure Termux-X11 app is installed and running")
        print("2. Grant necessary permissions:")
        print("   - termux-setup-storage")
        print("   - Allow display overlay permission")
        print("\n🎯 Quick Start:")
        print("  GUI Mode:    python termux_desktop_launcher.py --gui")
        print("  CLI Mode:    python main.py --cli")
        print("  Auto Mode:   python main.py")
        print("\n🔧 Troubleshooting:")
        print("  - If GUI doesn't open, check Termux-X11 app")
        print("  - Ensure all dependencies are installed")
        print("  - Run with --verbose for detailed logs")
        print("="*50 + "\n")
    
    def run(self, mode='auto'):
        """Main launcher function"""
        if not self.check_termux_environment():
            logger.error("Not running in Termux environment")
            return 1
        
        self.show_termux_instructions()
        
        if mode == 'gui':
            # Setup X11 environment
            if not self.check_x11_availability():
                logger.error("Termux-X11 not available. Please install it first.")
                print("📦 Install Termux-X11:")
                print("  pkg install x11-repo")
                print("  pkg install termux-x11-nightly")
                return 1
            
            # Start X11 server
            if not self.start_x11_server():
                logger.error("Failed to start X11 server")
                return 1
            
            # Setup display environment
            self.setup_display_environment()
            
            try:
                # Launch GUI
                return self.launch_api_tester_gui()
            finally:
                # Cleanup
                self.stop_x11_server()
                
        elif mode == 'cli':
            from main import UniversalAPITester
            tester = UniversalAPITester()
            return tester.run_cli_mode(None)
        else:
            # Auto mode - try GUI first, fallback to CLI
            if self.check_x11_availability():
                logger.info("X11 available, attempting GUI mode...")
                return self.run('gui')
            else:
                logger.info("X11 not available, using CLI mode...")
                return self.run('cli')

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal API Tester - Termux Launcher')
    parser.add_argument('--gui', action='store_true', help='Launch in GUI mode')
    parser.add_argument('--cli', action='store_true', help='Launch in CLI mode')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    launcher = TermuxDesktopLauncher()
    
    if args.gui:
        return launcher.run('gui')
    elif args.cli:
        return launcher.run('cli')
    else:
        return launcher.run('auto')

if __name__ == '__main__':
    sys.exit(main())
