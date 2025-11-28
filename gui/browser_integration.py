"""
Browser Integration GUI Component
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QComboBox, QTextEdit,
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import QProcess, QTimer
import os
import subprocess

from integration.browser_launcher import BrowserLauncher

logger = logging.getLogger(__name__)

class BrowserIntegration(QWidget):
    """Browser Integration Widget"""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.browser_process = None
        self.browser_launcher = BrowserLauncher(config)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Browser controls
        controls_group = QGroupBox("Browser Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Browser selection
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Browser:"))
        
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Firefox", "Chromium", "Chrome"])
        browser_layout.addWidget(self.browser_combo)
        
        self.launch_btn = QPushButton("🚀 Launch Browser")
        self.launch_btn.clicked.connect(self.launch_browser)
        browser_layout.addWidget(self.launch_btn)
        
        self.stop_btn = QPushButton("🛑 Stop Browser")
        self.stop_btn.clicked.connect(self.stop_browser)
        self.stop_btn.setEnabled(False)
        browser_layout.addWidget(self.stop_btn)
        
        controls_layout.addLayout(browser_layout)
        
        # Browser status
        self.status_label = QLabel("Status: Not running")
        controls_layout.addWidget(self.status_label)
        
        layout.addWidget(controls_group)
        
        # DevTools integration
        devtools_group = QGroupBox("DevTools Integration")
        devtools_layout = QVBoxLayout(devtools_group)
        
        # Import controls
        import_layout = QHBoxLayout()
        
        self.import_clipboard_btn = QPushButton("📋 Import from Clipboard")
        self.import_clipboard_btn.clicked.connect(self.import_from_clipboard)
        import_layout.addWidget(self.import_clipboard_btn)
        
        self.import_file_btn = QPushButton("📁 Import from File")
        self.import_file_btn.clicked.connect(self.import_from_file)
        import_layout.addWidget(self.import_file_btn)
        
        devtools_layout.addLayout(import_layout)
        
        # DevTools data display
        self.devtools_display = QTextEdit()
        self.devtools_display.setPlaceholderText("DevTools data will appear here...")
        self.devtools_display.setMaximumHeight(200)
        devtools_layout.addWidget(self.devtools_display)
        
        layout.addWidget(devtools_group)
        
        # Browser output
        output_group = QGroupBox("Browser Output")
        output_layout = QVBoxLayout(output_group)
        
        self.browser_output = QTextEdit()
        self.browser_output.setReadOnly(True)
        self.browser_output.setMaximumHeight(150)
        output_layout.addWidget(self.browser_output)
        
        layout.addWidget(output_group)
        
        layout.addStretch()
    
    def launch_browser(self):
        """Launch the selected browser"""
        browser = self.browser_combo.currentText().lower()
        
        try:
            self.status_label.setText(f"Status: Launching {browser}...")
            self.launch_btn.setEnabled(False)
            
            if browser == "firefox":
                success = self.browser_launcher.launch_firefox()
            elif browser == "chromium":
                success = self.browser_launcher.launch_chromium()
            else:  # chrome
                success = self.browser_launcher.launch_chrome()
            
            if success:
                self.status_label.setText(f"Status: {browser.capitalize()} running")
                self.stop_btn.setEnabled(True)
                self.add_output(f"{browser.capitalize()} browser launched successfully")
                
                # Start monitoring browser process
                self.start_browser_monitoring()
                
            else:
                self.status_label.setText(f"Status: Failed to launch {browser}")
                self.launch_btn.setEnabled(True)
                self.add_output(f"Failed to launch {browser} browser")
                QMessageBox.warning(self, "Browser Error", 
                                  f"Could not launch {browser} browser. "
                                  f"Make sure it's installed and available in PATH.")
                
        except Exception as e:
            self.status_label.setText("Status: Error occurred")
            self.launch_btn.setEnabled(True)
            self.add_output(f"Error launching browser: {str(e)}")
            QMessageBox.critical(self, "Browser Error", f"An error occurred:\n{str(e)}")
    
    def stop_browser(self):
        """Stop the running browser"""
        try:
            if self.browser_launcher.stop_browser():
                self.status_label.setText("Status: Browser stopped")
                self.launch_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.add_output("Browser stopped successfully")
            else:
                self.add_output("Failed to stop browser")
                
        except Exception as e:
            self.add_output(f"Error stopping browser: {str(e)}")
            QMessageBox.critical(self, "Browser Error", f"An error occurred while stopping browser:\n{str(e)}")
    
    def start_browser_monitoring(self):
        """Start monitoring browser process"""
        # This would typically monitor the browser process
        # For now, we'll just set a timer to check status
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_browser_status)
        self.monitor_timer.start(5000)  # Check every 5 seconds
    
    def check_browser_status(self):
        """Check if browser is still running"""
        if not self.browser_launcher.is_browser_running():
            self.status_label.setText("Status: Browser not running")
            self.launch_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.add_output("Browser process ended")
            self.monitor_timer.stop()
    
    def import_from_clipboard(self):
        """Import DevTools data from clipboard"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            text = clipboard.text().strip()
            
            if text:
                self.devtools_display.setPlainText(text)
                self.add_output("DevTools data imported from clipboard")
                
                # Auto-detect if it looks like DevTools data
                if any(keyword in text.lower() for keyword in ['http', 'api', 'request', 'response']):
                    self.add_output("✓ Detected potential API data")
                else:
                    self.add_output("⚠ Data doesn't look like DevTools output")
            else:
                QMessageBox.information(self, "Clipboard", "Clipboard is empty or contains no text.")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Could not import from clipboard:\n{str(e)}")
    
    def import_from_file(self):
        """Import DevTools data from file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open DevTools Log", "", 
                "Text Files (*.txt);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.devtools_display.setPlainText(content)
                
                self.add_output(f"DevTools data imported from: {file_path}")
                
                # Analyze file content
                lines = content.split('\n')
                api_count = sum(1 for line in lines if 'http' in line.lower() and ('api' in line.lower() or 'rest' in line.lower()))
                self.add_output(f"✓ Found {api_count} potential API endpoints")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Could not import from file:\n{str(e)}")
    
    def add_output(self, message):
        """Add message to output display"""
        current_text = self.browser_output.toPlainText()
        new_text = f"{message}\n{current_text}"
        self.browser_output.setPlainText(new_text[:1000])  # Limit output
    
    def get_devtools_data(self):
        """Get the current DevTools data"""
        return self.devtools_display.toPlainText().strip()
    
    def clear_devtools_data(self):
        """Clear the DevTools data display"""
        self.devtools_display.clear()
        self.add_output("DevTools data cleared")
    
    def is_browser_running(self):
        """Check if browser is running"""
        return self.browser_launcher.is_browser_running()
