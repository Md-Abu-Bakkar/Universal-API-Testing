#!/usr/bin/env python3
"""
Universal API Tester - Main Entry Point
Automated API Detection, Testing, and Bot Code Generation Tool
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.api_scanner import APIScanner
    from core.login_handler import LoginHandler
    from gui.dashboard import Dashboard
    from utils.termux_helper import TermuxHelper
    from utils.config_manager import ConfigManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_tester.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UniversalAPITester:
    def __init__(self):
        self.config = ConfigManager()
        self.termux_helper = TermuxHelper()
        self.api_scanner = APIScanner()
        self.login_handler = LoginHandler()
        
    def run_cli_mode(self, args):
        """Run in command line interface mode"""
        logger.info("Starting CLI Mode")
        
        if args.input:
            self.process_input_file(args.input)
        elif args.login:
            self.handle_login_mode(args)
        else:
            self.show_interactive_cli()
    
    def run_gui_mode(self):
        """Run in graphical user interface mode"""
        logger.info("Starting GUI Mode")
        
        # Check if Termux-X11 is available for Android
        if self.termux_helper.is_termux_environment():
            if not self.termux_helper.check_x11_availability():
                logger.warning("Termux-X11 not available. Falling back to basic GUI.")
                return self.run_basic_gui()
        
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
            dashboard = Dashboard()
            dashboard.show()
            return app.exec_()
        except ImportError as e:
            logger.error(f"GUI dependencies not available: {e}")
            return self.run_basic_gui()
    
    def run_basic_gui(self):
        """Fallback basic GUI using tkinter or terminal UI"""
        logger.info("Starting Basic GUI Mode")
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox, scrolledtext
            
            root = tk.Tk()
            root.title("Universal API Tester - Basic GUI")
            root.geometry("800x600")
            
            # Create main frame
            main_frame = ttk.Frame(root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Title
            title_label = ttk.Label(main_frame, text="Universal API Tester", 
                                  font=("Arial", 16, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, pady=10)
            
            # Input area
            input_label = ttk.Label(main_frame, text="Paste DevTools Data:")
            input_label.grid(row=1, column=0, sticky=tk.W, pady=5)
            
            input_text = scrolledtext.ScrolledText(main_frame, width=80, height=15)
            input_text.grid(row=2, column=0, columnspan=2, pady=5)
            
            # Buttons
            def analyze_data():
                data = input_text.get("1.0", tk.END)
                if data.strip():
                    try:
                        apis = self.api_scanner.extract_apis(data)
                        results = self.api_scanner.test_sequential(apis)
                        self.display_tkinter_results(results)
                    except Exception as e:
                        messagebox.showerror("Error", f"Analysis failed: {e}")
                else:
                    messagebox.showwarning("Warning", "Please enter some data to analyze")
            
            analyze_btn = ttk.Button(main_frame, text="Analyze APIs", command=analyze_data)
            analyze_btn.grid(row=3, column=0, pady=10)
            
            root.mainloop()
            
        except ImportError:
            # Fallback to terminal UI
            self.show_interactive_cli()
    
    def process_input_file(self, file_path):
        """Process input file with DevTools data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                devtools_data = f.read()
            
            apis = self.api_scanner.extract_apis(devtools_data)
            results = self.api_scanner.test_sequential(apis)
            
            self.display_results(results)
            
        except Exception as e:
            logger.error(f"Error processing input file: {e}")
    
    def handle_login_mode(self, args):
        """Handle login-based API testing"""
        credentials = {
            'username': args.username,
            'password': args.password,
            'url': args.url
        }
        
        if self.login_handler.detect_mode(credentials):
            session = self.login_handler.login_mode(credentials)
            if session:
                self.test_apis_with_session(session, args.url)
        else:
            self.login_handler.direct_api_mode(args.url)
    
    def show_interactive_cli(self):
        """Show interactive command line interface"""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich import print as rprint
            
            console = Console()
            
            rprint(Panel.fit(
                "[bold blue]Universal API Tester[/bold blue]\n"
                "Automated API Detection and Testing Tool",
                subtitle="🚀 Ready to scan APIs"
            ))
            
            # Interactive menu implementation
            choices = {
                '1': 'Import DevTools Log',
                '2': 'Login Mode Testing',
                '3': 'Direct API Testing',
                '4': 'Browser Integration',
                '5': 'Exit'
            }
            
            while True:
                console.print("\n[bold]Main Menu:[/bold]")
                for key, value in choices.items():
                    console.print(f"  {key}. {value}")
                
                choice = console.input("\n📝 Enter your choice: ").strip()
                
                if choice == '1':
                    self.handle_devtools_import()
                elif choice == '2':
                    self.handle_interactive_login()
                elif choice == '3':
                    self.handle_direct_testing()
                elif choice == '4':
                    self.launch_browser_integration()
                elif choice == '5':
                    console.print("👋 Goodbye!")
                    break
                else:
                    console.print("❌ Invalid choice. Please try again.")
                    
        except ImportError:
            # Basic terminal interface
            self.show_basic_cli()
    
    def show_basic_cli(self):
        """Basic terminal interface without rich"""
        print("=" * 50)
        print("Universal API Tester")
        print("=" * 50)
        
        while True:
            print("\nMain Menu:")
            print("1. Import DevTools Log")
            print("2. Login Mode Testing") 
            print("3. Direct API Testing")
            print("4. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                file_path = input("Enter DevTools log file path: ").strip()
                if os.path.exists(file_path):
                    self.process_input_file(file_path)
                else:
                    print("File not found!")
            elif choice == '2':
                self.handle_interactive_login()
            elif choice == '3':
                print("Direct API testing selected")
                # Implement direct testing
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")
    
    def handle_devtools_import(self):
        """Handle DevTools log import"""
        from rich.console import Console
        console = Console()
        
        file_path = console.input("📁 Enter DevTools log file path: ").strip()
        if os.path.exists(file_path):
            self.process_input_file(file_path)
        else:
            console.print("❌ File not found!")
    
    def handle_interactive_login(self):
        """Handle interactive login"""
        from rich.console import Console
        console = Console()
        
        url = console.input("🌐 Enter target URL: ").strip()
        username = console.input("👤 Username: ").strip()
        password = console.input("🔑 Password: ").strip()
        
        credentials = {
            'username': username,
            'password': password,
            'url': url
        }
        
        self.handle_login_mode(argparse.Namespace(
            login=True, username=username, 
            password=password, url=url
        ))
    
    def handle_direct_testing(self):
        """Handle direct API testing"""
        from rich.console import Console
        console = Console()
        
        url = console.input("🌐 Enter API URL to test: ").strip()
        if url:
            try:
                # Test single API
                api_info = {
                    'url': url,
                    'method': 'GET',
                    'type': 'UNKNOWN'
                }
                result = self.api_scanner._test_single_api(api_info)
                self.display_results([result])
            except Exception as e:
                console.print(f"❌ Error testing API: {e}")
    
    def launch_browser_integration(self):
        """Launch browser integration"""
        try:
            from integration.browser_launcher import BrowserLauncher
            browser_launcher = BrowserLauncher()
            browser_launcher.launch_browser_choice()
        except ImportError as e:
            logger.error(f"Browser integration not available: {e}")
            from rich.console import Console
            console = Console()
            console.print("❌ Browser integration not available")
    
    def test_apis_with_session(self, session, base_url):
        """Test APIs with established session"""
        logger.info(f"Testing APIs with session for {base_url}")
        # Implementation for session-based testing
        pass
    
    def display_results(self, results):
        """Display API testing results"""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import print as rprint
            
            console = Console()
            
            table = Table(title="API Testing Results")
            table.add_column("API", style="cyan")
            table.add_column("Status", justify="center")
            table.add_column("Type", style="magenta")
            table.add_column("Response", style="green")
            
            for result in results:
                status_icon = "✅" if result.get('success', False) else "❌"
                api_url = result.get('api', 'Unknown')
                api_type = result.get('type', 'UNKNOWN')
                response_preview = result.get('response', '')[:50] + "..." if len(result.get('response', '')) > 50 else result.get('response', '')
                
                table.add_row(
                    api_url,
                    status_icon,
                    api_type,
                    response_preview
                )
            
            console.print(table)
            
        except ImportError:
            # Basic table display
            print("\nAPI Testing Results:")
            print("-" * 80)
            print(f"{'API':<40} {'Status':<10} {'Type':<15} {'Response'}")
            print("-" * 80)
            for result in results:
                status = "SUCCESS" if result.get('success', False) else "FAILED"
                print(f"{result.get('api', 'Unknown'):<40} {status:<10} {result.get('type', 'UNKNOWN'):<15} {result.get('response', '')[:30]}")
    
    def display_tkinter_results(self, results):
        """Display results in tkinter window"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        result_window = tk.Toplevel()
        result_window.title("API Testing Results")
        result_window.geometry("900x500")
        
        # Create treeview
        tree = ttk.Treeview(result_window, columns=('Status', 'Type', 'Response'), show='headings')
        tree.heading('#0', text='API URL')
        tree.heading('Status', text='Status')
        tree.heading('Type', text='Type')
        tree.heading('Response', text='Response')
        
        tree.column('#0', width=400)
        tree.column('Status', width=80)
        tree.column('Type', width=100)
        tree.column('Response', width=300)
        
        # Add results
        for result in results:
            status = "✅" if result.get('success', False) else "❌"
            tree.insert('', 'end', text=result.get('api', 'Unknown'), 
                       values=(status, result.get('type', 'UNKNOWN'), 
                              result.get('response', '')[:50]))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Close button
        close_btn = ttk.Button(result_window, text="Close", command=result_window.destroy)
        close_btn.pack(pady=10)

def main():
    parser = argparse.ArgumentParser(
        description="Universal API Tester - Automated API Detection and Testing Tool"
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Run in command line interface mode'
    )
    
    parser.add_argument(
        '--gui', 
        action='store_true',
        help='Run in graphical user interface mode'
    )
    
    parser.add_argument(
        '--input', 
        type=str,
        help='Input file with DevTools data'
    )
    
    parser.add_argument(
        '--login', 
        action='store_true',
        help='Enable login mode'
    )
    
    parser.add_argument(
        '--username', 
        type=str,
        help='Username for login'
    )
    
    parser.add_argument(
        '--password', 
        type=str,
        help='Password for login'
    )
    
    parser.add_argument(
        '--url', 
        type=str,
        help='Target URL for testing'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create tester instance
    tester = UniversalAPITester()
    
    # Determine run mode
    if args.gui:
        tester.run_gui_mode()
    elif args.cli or args.input or args.login:
        tester.run_cli_mode(args)
    else:
        # Auto-detect mode
        if os.getenv('DISPLAY') or TermuxHelper().check_x11_availability():
            tester.run_gui_mode()
        else:
            tester.run_cli_mode(args)

if __name__ == "__main__":
    main()
