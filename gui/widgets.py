"""
Custom Widgets for Universal API Tester
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
                             QPushButton, QProgressBar, QTreeWidget, QTreeWidgetItem,
                             QHeaderView, QSplitter, QComboBox, QLineEdit,
                             QCheckBox, QSpinBox, QDoubleSpinBox, QScrollArea,
                             QFrame, QTabWidget, QToolButton, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import json

class ApiResultWidget(QWidget):
    """Widget for displaying API testing results"""
    
    api_selected = pyqtSignal(dict)  # Signal when API is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_results = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Summary section
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        self.total_label = QLabel("Total: 0")
        self.success_label = QLabel("✅ Success: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.success_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addStretch()
        
        layout.addWidget(summary_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Status", "API", "Type", "Method", "Code", "Size"
        ])
        
        # Set column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # API
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Method
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Code
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Size
        
        self.results_table.doubleClicked.connect(self.on_api_double_click)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.results_table)
    
    def set_results(self, results):
        """Set API results and update display"""
        self.api_results = results
        self.update_display()
    
    def update_display(self):
        """Update the results display"""
        self.results_table.setRowCount(len(self.api_results))
        
        successful = 0
        failed = 0
        
        for row, result in enumerate(self.api_results):
            # Status
            status = "✅" if result.get('success', False) else "❌"
            status_item = QTableWidgetItem(status)
            self.results_table.setItem(row, 0, status_item)
            
            # API URL
            url = result.get('api', 'Unknown')
            url_item = QTableWidgetItem(url)
            self.results_table.setItem(row, 1, url_item)
            
            # Type
            type_item = QTableWidgetItem(result.get('type', 'UNKNOWN'))
            self.results_table.setItem(row, 2, type_item)
            
            # Method
            method_item = QTableWidgetItem(result.get('method', 'GET'))
            self.results_table.setItem(row, 3, method_item)
            
            # Status code
            code = result.get('status_code', 0)
            code_item = QTableWidgetItem(str(code) if code else 'N/A')
            self.results_table.setItem(row, 4, code_item)
            
            # Response size
            size = result.get('size', 0)
            size_text = f"{size} bytes" if size else "N/A"
            size_item = QTableWidgetItem(size_text)
            self.results_table.setItem(row, 5, size_item)
            
            # Count success/failure
            if result.get('success', False):
                successful += 1
            else:
                failed += 1
        
        # Update summary
        self.total_label.setText(f"Total: {len(self.api_results)}")
        self.success_label.setText(f"✅ Success: {successful}")
        self.failed_label.setText(f"❌ Failed: {failed}")
    
    def on_api_double_click(self, index):
        """Handle double click on API result"""
        row = index.row()
        if 0 <= row < len(self.api_results):
            self.api_selected.emit(self.api_results[row])
    
    def get_selected_api(self):
        """Get currently selected API"""
        current_row = self.results_table.currentRow()
        if 0 <= current_row < len(self.api_results):
            return self.api_results[current_row]
        return None
    
    def clear_results(self):
        """Clear all results"""
        self.api_results = []
        self.results_table.setRowCount(0)
        self.total_label.setText("Total: 0")
        self.success_label.setText("✅ Success: 0")
        self.failed_label.setText("❌ Failed: 0")

class CodePreviewWidget(QWidget):
    """Widget for previewing and editing generated code"""
    
    code_changed = pyqtSignal(str)  # Signal when code is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_code = ""
        self.is_readonly = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self.copy_code)
        toolbar_layout.addWidget(self.copy_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_code)
        toolbar_layout.addWidget(self.save_btn)
        
        self.format_btn = QPushButton("✨ Format")
        self.format_btn.clicked.connect(self.format_code)
        toolbar_layout.addWidget(self.format_btn)
        
        toolbar_layout.addStretch()
        
        # Language indicator
        self.lang_label = QLabel("Python")
        toolbar_layout.addWidget(self.lang_label)
        
        layout.addLayout(toolbar_layout)
        
        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.textChanged.connect(self.on_code_changed)
        
        # Use monospace font for code
        font = QFont("Courier", 10)
        self.code_editor.setFont(font)
        
        layout.addWidget(self.code_editor)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def set_code(self, code, language="python"):
        """Set the code content"""
        self.current_code = code
        self.code_editor.setPlainText(code)
        self.lang_label.setText(language.capitalize())
        
        # Set appropriate syntax highlighting (basic)
        self.apply_syntax_highlighting(language)
    
    def get_code(self):
        """Get the current code"""
        return self.code_editor.toPlainText()
    
    def set_readonly(self, readonly):
        """Set read-only mode"""
        self.is_readonly = readonly
        self.code_editor.setReadOnly(readonly)
        
        if readonly:
            self.code_editor.setStyleSheet("background: #f5f5f5;")
            self.status_label.setText("Read-only mode")
        else:
            self.code_editor.setStyleSheet("")
            self.status_label.setText("Edit mode")
    
    def copy_code(self):
        """Copy code to clipboard"""
        code = self.get_code()
        if code:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(code)
            self.status_label.setText("Code copied to clipboard")
    
    def save_code(self):
        """Save code to file"""
        code = self.get_code()
        if not code:
            self.status_label.setText("No code to save")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Code", "", 
            "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.status_label.setText(f"Code saved to {file_path}")
            except Exception as e:
                self.status_label.setText(f"Error saving: {str(e)}")
    
    def format_code(self):
        """Format the code (basic implementation)"""
        code = self.get_code()
        
        # Basic Python formatting
        if self.lang_label.text().lower() == "python":
            # Indentation cleanup
            lines = code.split('\n')
            formatted_lines = []
            
            for line in lines:
                # Remove excessive whitespace
                line = line.rstrip()
                formatted_lines.append(line)
            
            formatted_code = '\n'.join(formatted_lines)
            self.set_code(formatted_code, "python")
            self.status_label.setText("Code formatted")
        else:
            self.status_label.setText("Formatting not supported for this language")
    
    def apply_syntax_highlighting(self, language):
        """Apply basic syntax highlighting"""
        # This is a very basic implementation
        # For production, consider using QSyntaxHighlighter or external libraries
        
        if language.lower() == "python":
            # Set a style that works well for code
            self.code_editor.setStyleSheet("""
                QTextEdit {
                    background: #1e1e1e;
                    color: #d4d4d4;
                    font-family: 'Courier New', monospace;
                }
            """)
        else:
            self.code_editor.setStyleSheet("""
                QTextEdit {
                    background: #f8f8f8;
                    color: #333;
                    font-family: 'Courier New', monospace;
                }
            """)
    
    def on_code_changed(self):
        """Handle code changes"""
        new_code = self.get_code()
        if new_code != self.current_code:
            self.current_code = new_code
            self.code_changed.emit(new_code)
            
            # Update line count
            lines = new_code.split('\n')
            self.status_label.setText(f"Lines: {len(lines)}")

class SessionManagerWidget(QWidget):
    """Widget for managing API sessions"""
    
    session_selected = pyqtSignal(str)  # Signal when session is selected
    session_deleted = pyqtSignal(str)  # Signal when session is deleted
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.sessions = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_sessions)
        controls_layout.addWidget(self.refresh_btn)
        
        self.new_btn = QPushButton("➕ New Session")
        self.new_btn.clicked.connect(self.create_session)
        controls_layout.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_session)
        controls_layout.addWidget(self.delete_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_session)
        controls_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_session)
        controls_layout.addWidget(self.export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Sessions tree
        self.sessions_tree = QTreeWidget()
        self.sessions_tree.setHeaderLabels([
            "Session ID", "Created", "Status", "APIs"
        ])
        
        self.sessions_tree.itemDoubleClicked.connect(self.on_session_double_click)
        layout.addWidget(self.sessions_tree)
        
        # Session details
        details_group = QGroupBox("Session Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
    
    def refresh_sessions(self):
        """Refresh sessions list"""
        # This would typically load from session manager
        # For now, we'll use mock data
        self.sessions_tree.clear()
        
        # Mock sessions
        mock_sessions = {
            "session_1": {
                "created": "2024-01-15 10:30:00",
                "status": "active",
                "apis": 5,
                "details": {"url": "https://example.com", "user": "admin"}
            },
            "session_2": {
                "created": "2024-01-15 11:45:00", 
                "status": "expired",
                "apis": 3,
                "details": {"url": "https://api.example.com", "user": "test"}
            }
        }
        
        for session_id, session_data in mock_sessions.items():
            item = QTreeWidgetItem(self.sessions_tree)
            item.setText(0, session_id)
            item.setText(1, session_data["created"])
            item.setText(2, session_data["status"])
            item.setText(3, str(session_data["apis"]))
            
            # Store session data in item
            item.setData(0, Qt.UserRole, session_data)
        
        self.sessions = mock_sessions
    
    def create_session(self):
        """Create a new session"""
        # This would typically open a dialog to configure new session
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, "New Session", "Enter session name:"
        )
        
        if ok and name:
            # Create new session
            session_id = f"session_{len(self.sessions) + 1}"
            self.sessions[session_id] = {
                "created": "2024-01-15 12:00:00",
                "status": "new",
                "apis": 0,
                "details": {"name": name}
            }
            
            self.refresh_sessions()
    
    def delete_session(self):
        """Delete selected session"""
        current_item = self.sessions_tree.currentItem()
        if current_item:
            session_id = current_item.text(0)
            
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete session '{session_id}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    self.refresh_sessions()
                    self.session_deleted.emit(session_id)
                    self.details_text.clear()
    
    def import_session(self):
        """Import session from file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Session", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get('id', f"imported_{len(self.sessions)}")
                self.sessions[session_id] = session_data
                self.refresh_sessions()
                
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Import Error", f"Could not import session:\n{str(e)}")
    
    def export_session(self):
        """Export selected session to file"""
        current_item = self.sessions_tree.currentItem()
        if not current_item:
            return
        
        session_id = current_item.text(0)
        session_data = self.sessions.get(session_id)
        
        if not session_data:
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Session", f"{session_id}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                session_data['id'] = session_id
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Successful", f"Session exported to:\n{file_path}")
                
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Export Error", f"Could not export session:\n{str(e)}")
    
    def on_session_double_click(self, item, column):
        """Handle session double click"""
        session_id = item.text(0)
        session_data = item.data(0, Qt.UserRole)
        
        if session_data:
            # Display session details
            details = f"Session: {session_id}\n"
            details += f"Created: {session_data.get('created', 'Unknown')}\n"
            details += f"Status: {session_data.get('status', 'Unknown')}\n"
            details += f"APIs: {session_data.get('apis', 0)}\n\n"
            
            # Add detailed info
            details_info = session_data.get('details', {})
            for key, value in details_info.items():
                details += f"{key}: {value}\n"
            
            self.details_text.setPlainText(details)
            self.session_selected.emit(session_id)

class ConfigEditorWidget(QWidget):
    """Widget for editing configuration"""
    
    config_changed = pyqtSignal(dict)  # Signal when config changes
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.original_config = config.copy() if config else {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_config)
        controls_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_config)
        controls_layout.addWidget(self.reset_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_config)
        controls_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_config)
        controls_layout.addWidget(self.export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Config editor
        self.config_editor = QTextEdit()
        self.config_editor.textChanged.connect(self.on_config_changed)
        
        # Use monospace font for JSON
        font = QFont("Courier", 10)
        self.config_editor.setFont(font)
        
        layout.addWidget(self.config_editor)
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Load current config
        self.load_config()
    
    def load_config(self):
        """Load configuration into editor"""
        try:
            config_json = json.dumps(self.config, indent=2)
            self.config_editor.setPlainText(config_json)
            self.status_label.setText("Configuration loaded")
        except Exception as e:
            self.status_label.setText(f"Error loading config: {str(e)}")
    
    def save_config(self):
        """Save configuration from editor"""
        try:
            config_json = self.config_editor.toPlainText()
            new_config = json.loads(config_json)
            
            self.config = new_config
            self.original_config = new_config.copy()
            
            self.config_changed.emit(new_config)
            self.status_label.setText("Configuration saved")
            
        except json.JSONDecodeError as e:
            self.status_label.setText(f"Invalid JSON: {str(e)}")
        except Exception as e:
            self.status_label.setText(f"Error saving config: {str(e)}")
    
    def reset_config(self):
        """Reset to original configuration"""
        self.config = self.original_config.copy()
        self.load_config()
        self.status_label.setText("Configuration reset")
    
    def import_config(self):
        """Import configuration from file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    new_config = json.load(f)
                
                self.config = new_config
                self.original_config = new_config.copy()
                self.load_config()
                self.config_changed.emit(new_config)
                
                self.status_label.setText(f"Configuration imported from {file_path}")
                
            except Exception as e:
                self.status_label.setText(f"Error importing config: {str(e)}")
    
    def export_config(self):
        """Export configuration to file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "api_tester_config.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                self.status_label.setText(f"Configuration exported to {file_path}")
                
            except Exception as e:
                self.status_label.setText(f"Error exporting config: {str(e)}")
    
    def on_config_changed(self):
        """Handle configuration changes"""
        # Check if config is valid JSON
        try:
            config_json = self.config_editor.toPlainText()
            json.loads(config_json)
            self.status_label.setText("Valid JSON")
        except:
            self.status_label.setText("Invalid JSON")
    
    def set_config(self, config):
        """Set new configuration"""
        self.config = config
        self.original_config = config.copy()
        self.load_config()
