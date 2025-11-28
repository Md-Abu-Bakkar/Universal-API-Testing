#!/usr/bin/env python3
"""
Enhanced CLI for Termux - Rich terminal interface
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import box
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.api_scanner import APIScanner
from core.code_generator import CodeGenerator

console = Console()

class EnhancedCLI:
    def __init__(self):
        self.scanner = APIScanner()
        self.code_gen = CodeGenerator()
    
    def show_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                UNIVERSAL API TESTER - TERMUX                ║
║                  Automated API Detection Tool               ║
╚══════════════════════════════════════════════════════════════╝
"""
        console.print(Panel(banner, style="bold blue", box=box.DOUBLE))
    
    def main_menu(self):
        while True:
            console.print("\n" + "="*60)
            console.print("[bold cyan]🏠 MAIN MENU[/bold cyan]")
            console.print("="*60)
            
            menu_options = [
                "[1] 🔍 Scan APIs from DevTools Data",
                "[2] 📁 Import from File", 
                "[3] 🌐 Direct URL Testing",
                "[4] 💻 Generate Bot Code",
                "[5] 🚪 Exit"
            ]
            
            for option in menu_options:
                console.print(option)
            
            choice = Prompt.ask("\n📝 Select option", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.scan_apis()
            elif choice == "2":
                self.import_from_file()
            elif choice == "3":
                self.direct_testing()
            elif choice == "4":
                self.generate_code()
            else:
                console.print("👋 Goodbye!")
                break
    
    def scan_apis(self):
        console.print("\n[bold green]🔍 API SCANNER[/bold green]")
        console.print("-" * 40)
        
        devtools_data = Prompt.ask("📋 Paste DevTools data\n", multiline=True)
        
        if not devtools_data.strip():
            console.print("[red]❌ No data provided![/red]")
            return
        
        with console.status("[bold green]Scanning APIs...", spinner="dots"):
            apis = self.scanner.extract_apis(devtools_data)
            results = self.scanner.test_sequential(apis)
        
        self.display_results(results)
        
        # Store results for code generation
        self.last_results = results
    
    def display_results(self, results):
        console.print(f"\n[bold green]📊 SCAN RESULTS[/bold green]")
        console.print(f"Found [bold]{len(results)}[/bold] APIs")
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Status", width=8)
        table.add_column("Method", width=8)
        table.add_column("URL", width=50)
        table.add_column("Type", width=12)
        table.add_column("Code", width=6)
        
        successful = 0
        for result in results:
            status = "✅" if result.get('success') else "❌"
            if result.get('success'):
                successful += 1
            
            # Shorten long URLs for display
            url = result.get('api', 'N/A')
            if len(url) > 45:
                url = url[:42] + "..."
            
            table.add_row(
                status,
                result.get('method', 'GET'),
                url,
                result.get('type', 'UNKNOWN'),
                str(result.get('status_code', 'N/A'))
            )
        
        console.print(table)
        console.print(f"\n[green]✅ Successful: {successful}[/green] | [red]❌ Failed: {len(results)-successful}[/red]")
    
    def generate_code(self):
        if not hasattr(self, 'last_results') or not self.last_results:
            console.print("[red]❌ No scan results available. Please scan APIs first.[/red]")
            return
        
        console.print("\n[bold blue]💻 CODE GENERATOR[/bold blue]")
        console.print("-" * 40)
        
        templates = {
            "1": ("Python Requests", "requests"),
            "2": ("Python aiohttp", "aiohttp"), 
            "3": ("cURL Commands", "curl"),
            "4": ("Bot Template", "bot")
        }
        
        for key, (name, _) in templates.items():
            console.print(f"[{key}] {name}")
        
        choice = Prompt.ask("\nSelect template", choices=list(templates.keys()))
        
        template_name, template_type = templates[choice]
        
        with console.status(f"Generating {template_name} code...", spinner="dots"):
            if template_type == "bot":
                code = self.code_gen.generate_bot_template(self.last_results)
            elif template_type == "curl":
                commands = self.code_gen.generate_curl_commands(self.last_results)
                code = "\n".join(commands)
            else:
                code = self.code_gen.generate_python_code(self.last_results, template_type)
        
        console.print(f"\n[bold green]📄 GENERATED CODE - {template_name}[/bold green]")
        console.print(Panel(code, style="green", title="Code Output"))
        
        # Save to file option
        if Prompt.ask("\n💾 Save to file?", choices=["y", "n"]) == "y":
            filename = Prompt.ask("Enter filename")
            try:
                with open(filename, 'w') as f:
                    f.write(code)
                console.print(f"[green]✅ Code saved to {filename}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error saving file: {e}[/red]")

def main():
    cli = EnhancedCLI()
    cli.show_banner()
    cli.main_menu()

if __name__ == "__main__":
    main()
