"""
Log Viewer GUI Component
"""

import logging
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QTextEdit, QPushButton, QComboBox, QLabel,
                             QCheckBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QTextCursor, QFont

logger = logging.getLogger(__name__)

class LogViewer(QWidget):
    """Log Viewer Widget for monitoring application logs"""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.log_file = self.config.get('logging', {}).get('file_path', 'api_tester.log')
        self.auto_refresh = True
        self.refresh_interval = 2000  # 2 seconds
        
        self.init_ui()
        self.setup_log_monitoring()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_group = QGroupBox("Log Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Log level filter
        controls_layout.addWidget(QLabel("Log Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(self.level_combo)
        
        # Auto-refresh
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_check)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(self.refresh_btn)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(self.clear_btn)
        
        # Export button
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self.export_logs)
        controls_layout.addWidget(self.export_btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Log display
        log_group = QGroupBox("Application Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Use monospace font for logs
        font = QFont("Courier", 9)
        self.log_display.setFont(font)
        
        log_layout.addWidget(self.log_display)
        layout.addWidget(log_group)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.line_count_label = QLabel("Lines: 0")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.line_count_label)
        
        layout.addLayout(status_layout)
    
    def setup_log_monitoring(self):
        """Setup log file monitoring"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        if self.auto_refresh:
            self.refresh_timer.start(self.refresh_interval)
        
        # Load initial logs
        self.refresh_logs()
    
    def refresh_logs(self):
        """Refresh log display"""
        try:
            if not os.path.exists(self.log_file):
                self.log_display.setPlainText(f"Log file not found: {self.log_file}")
                self.status_label.setText("Log file not found")
                return
            
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Apply level filter
            filtered_content = self.apply_level_filter(content)
            
            # Check if content changed
            current_content = self.log_display.toPlainText()
            if filtered_content != current_content:
                # Save scroll position
                scrollbar = self.log_display.verticalScrollBar()
                was_at_bottom = scrollbar.value() == scrollbar.maximum()
                
                self.log_display.setPlainText(filtered_content)
                
                # Restore scroll position or scroll to bottom
                if was_at_bottom:
                    self.log_display.moveCursor(QTextCursor.End)
                else:
                    scrollbar.setValue(scrollbar.value())
            
            # Update line count
            lines = filtered_content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            self.line_count_label.setText(f"Lines: {len(non_empty_lines)}")
            
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"Error reading logs: {str(e)}")
            logger.error(f"Error refreshing logs: {e}")
    
    def apply_level_filter(self, content):
        """Apply log level filter to content"""
        selected_level = self.level_combo.currentText()
        
        if selected_level == "ALL":
            return content
        
        # Define level order for filtering
        level_order = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        min_level = level_order.get(selected_level, 20)
        
        filtered_lines = []
        for line in content.split('\n'):
            if not line.strip():
                filtered_lines.append(line)
                continue
            
            # Check if line contains log level
            line_upper = line.upper()
            line_level = 0
            
            for level, value in level_order.items():
                if level in line_upper:
                    line_level = value
                    break
            
            # Include line if it meets the level requirement or doesn't have a clear level
            if line_level == 0 or line_level >= min_level:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def filter_logs(self):
        """Apply log level filter"""
        self.refresh_logs()
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh"""
        self.auto_refresh = (state == 2)  # 2 is checked state
        
        if self.auto_refresh:
            self.refresh_timer.start(self.refresh_interval)
            self.status_label.setText("Auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.status_label.setText("Auto-refresh disabled")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
        self.line_count_label.setText("Lines: 0")
        self.status_label.setText("Logs cleared")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", 
                f"api_tester_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                content = self.log_display.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Logs exported to:\n{file_path}")
                self.status_label.setText(f"Logs exported to {os.path.basename(file_path)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Could not export logs:\n{str(e)}")
            self.status_label.setText("Export failed")
    
    def add_log_message(self, level, message):
        """Add a log message directly to the display"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Move cursor to end and insert
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(log_entry + '\n')
        
        # Auto-scroll to bottom
        self.log_display.moveCursor(QTextCursor.End)
        
        # Update line count
        current_text = self.log_display.toPlainText()
        lines = current_text.split('\n')
        self.line_count_label.setText(f"Lines: {len(lines) - 1}")
    
    def set_log_file(self, file_path):
        """Set the log file to monitor"""
        self.log_file = file_path
        self.refresh_logs()
    
    def get_current_logs(self):
        """Get current log content"""
        return self.log_display.toPlainText()
    
    def search_in_logs(self, search_text):
        """Search for text in logs"""
        if not search_text:
            return
        
        document = self.log_document()
        cursor = QTextCursor(document)
        
        # Clear previous highlights
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        # Search and highlight
        format = QTextCharFormat()
        format.setBackground(QColor('yellow'))
        
        while not cursor.isNull() and not cursor.atEnd():
            cursor = document.find(search_text, cursor)
            if not cursor.isNull():
                cursor.mergeCharFormat(format)
    
    def set_refresh_interval(self, interval_ms):
        """Set auto-refresh interval in milliseconds"""
        self.refresh_interval = interval_ms
        if self.auto_refresh:
            self.refresh_timer.stop()
            self.refresh_timer.start(interval_ms)
