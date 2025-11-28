"""
Main Dashboard GUI for Universal API Tester
"""

import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QTextEdit, QPushButton,
                             QLabel, QLineEdit, QComboBox, QGroupBox, QProgressBar,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog,
                             QToolBar, QAction, QStatusBar, QMenu, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import json
import os

from core.api_scanner import APIScanner
from core.login_handler import LoginHandler
from core.code_generator import CodeGenerator
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ScannerThread(QThread):
    """Thread for API scanning to prevent GUI freezing"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, devtools_data, config):
        super().__init__()
        self.devtools_data = devtools_data
        self.config = config
    
    def run(self):
        try:
            self.progress_signal.emit(10, "Initializing scanner...")
            
            scanner = APIScanner(self.config)
            
            self.progress_signal.emit(30, "Extracting APIs...")
            apis = scanner.extract_apis(self.devtools_data)
            
            self.progress_signal.emit(50, f"Testing {len(apis)} APIs...")
            results = scanner.test_sequential(apis)
            
            self.progress_signal.emit(100, "Scan completed!")
            self.finished_signal.emit(results)
            
        except Exception as e:
            self.error_signal.emit(str(e))

class Dashboard(QMainWindow):
    """Main Dashboard Window"""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or ConfigManager().config
        self.api_results = []
        self.current_session = None
        
        self.init_ui()
        self.setup_connections()
        
        logger.info("Dashboard initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Universal API Tester")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.apply_dark_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar
        self.create_sidebar(main_layout)
        
        # Create main content area
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply styles
        self.apply_styles()
    
    def create_sidebar(self, main_layout):
        """Create sidebar with navigation"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Logo/Title
        title_label = QLabel("API Tester")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #61afef;
                padding: 15px;
                border-bottom: 1px solid #3e4451;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔍 API Scanner", self.show_api_scanner),
            ("🔐 Login Manager", self.show_login_manager),
            ("💻 Code Generator", self.show_code_generator),
            ("🌐 Browser Integration", self.show_browser_integration),
            ("📋 Session Manager", self.show_session_manager),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: none;
                    background: transparent;
                    color: #abb2bf;
                }
                QPushButton:hover {
                    background: #3e4451;
                    color: #61afef;
                }
            """)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # System info
        sys_info = QGroupBox("System Info")
        sys_info.setStyleSheet("""
            QGroupBox {
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #61afef;
            }
        """)
        sys_layout = QVBoxLayout(sys_info)
        
        status_label = QLabel("🟢 Ready")
        session_label = QLabel("Session: Not logged in")
        
        sys_layout.addWidget(status_label)
        sys_layout.addWidget(session_label)
        
        sidebar_layout.addWidget(sys_info)
        
        main_layout.addWidget(sidebar)
    
    def create_main_content(self, main_layout):
        """Create main content area with tabs"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3e4451;
                background: #282c34;
            }
            QTabBar::tab {
                background: #3e4451;
                color: #abb2bf;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #61afef;
                color: #282c34;
            }
            QTabBar::tab:hover {
                background: #56b6c2;
            }
        """)
        
        # Create tabs
        self.dashboard_tab = self.create_dashboard_tab()
        self.scanner_tab = self.create_scanner_tab()
        self.login_tab = self.create_login_tab()
        self.code_tab = self.create_code_tab()
        self.browser_tab = self.create_browser_tab()
        self.sessions_tab = self.create_sessions_tab()
        self.settings_tab = self.create_settings_tab()
        
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tab_widget.addTab(self.scanner_tab, "🔍 API Scanner")
        self.tab_widget.addTab(self.login_tab, "🔐 Login")
        self.tab_widget.addTab(self.code_tab, "💻 Code Gen")
        self.tab_widget.addTab(self.browser_tab, "🌐 Browser")
        self.tab_widget.addTab(self.sessions_tab, "📋 Sessions")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Welcome section
        welcome_group = QGroupBox("Welcome to Universal API Tester")
        welcome_layout = QVBoxLayout(welcome_group)
        
        welcome_text = QLabel("""
        <h2>🚀 Universal API Tester</h2>
        <p>Automated API Detection, Testing, and Bot Code Generation Tool</p>
        <p><b>Quick Start:</b></p>
        <ol>
            <li>Go to <b>API Scanner</b> tab</li>
            <li>Paste DevTools data or import from file</li>
            <li>Click <b>Scan APIs</b> to detect endpoints</li>
            <li>Use <b>Code Generator</b> to create bot code</li>
        </ol>
        """)
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_log)
        
        layout.addWidget(activity_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        stats = [
            ("Total APIs Scanned", "0"),
            ("Successful APIs", "0"),
            ("Failed APIs", "0"),
            ("Code Generated", "0")
        ]
        
        for stat_name, stat_value in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            name_label = QLabel(stat_name)
            value_label = QLabel(stat_value)
            value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #61afef;")
            
            stat_layout.addWidget(name_label)
            stat_layout.addWidget(value_label)
            stats_layout.addWidget(stat_widget)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return widget
    
    def create_scanner_tab(self):
        """Create API scanner tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_group = QGroupBox("DevTools Data Input")
        input_layout = QVBoxLayout(input_group)
        
        # File import
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select DevTools log file...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        input_layout.addLayout(file_layout)
        
        # Manual input
        self.devtools_input = QTextEdit()
        self.devtools_input.setPlaceholderText("Paste DevTools network data here...")
        self.devtools_input.setMinimumHeight(300)
        input_layout.addWidget(self.devtools_input)
        
        layout.addWidget(input_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        scan_btn = QPushButton("🚀 Scan APIs")
        scan_btn.clicked.connect(self.start_scan)
        scan_btn.setStyleSheet("QPushButton { background: #98c379; color: black; font-weight: bold; }")
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_input)
        
        control_layout.addWidget(scan_btn)
        control_layout.addWidget(clear_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Results section
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["API", "Status", "Type", "Method", "Response"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_login_tab(self):
        """Create login manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Login form
        login_group = QGroupBox("Login Configuration")
        login_layout = QVBoxLayout(login_group)
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Target URL:"))
        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText("https://example.com/login")
        url_layout.addWidget(self.login_url_edit)
        login_layout.addLayout(url_layout)
        
        # Credentials
        cred_layout = QHBoxLayout()
        cred_layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        cred_layout.addWidget(self.username_edit)
        
        cred_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        cred_layout.addWidget(self.password_edit)
        
        login_layout.addLayout(cred_layout)
        
        # Login button
        login_btn = QPushButton("🔐 Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("QPushButton { background: #61afef; color: black; font-weight: bold; }")
        login_layout.addWidget(login_btn)
        
        layout.addWidget(login_group)
        
        # Session info
        session_group = QGroupBox("Session Information")
        session_layout = QVBoxLayout(session_group)
        
        self.session_info = QTextEdit()
        self.session_info.setReadOnly(True)
        self.session_info.setMaximumHeight(150)
        session_layout.addWidget(self.session_info)
        
        layout.addWidget(session_group)
        
        layout.addStretch()
        return widget
    
    def create_code_tab(self):
        """Create code generator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Template selection
        template_group = QGroupBox("Code Template")
        template_layout = QHBoxLayout(template_group)
        
        template_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Python Requests", "Python aiohttp", "cURL", "Bot Template"])
        template_layout.addWidget(self.template_combo)
        
        generate_btn = QPushButton("🔄 Generate Code")
        generate_btn.clicked.connect(self.generate_code)
        template_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_code)
        template_layout.addWidget(export_btn)
        
        template_layout.addStretch()
        layout.addWidget(template_group)
        
        # Generated code
        code_group = QGroupBox("Generated Code")
        code_layout = QVBoxLayout(code_group)
        
        self.generated_code = QTextEdit()
        self.generated_code.setPlaceholderText("Generated code will appear here...")
        code_layout.addWidget(self.generated_code)
        
        layout.addWidget(code_group)
        
        return widget
    
    def create_browser_tab(self):
        """Create browser integration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Browser controls
        browser_group = QGroupBox("Browser Integration")
        browser_layout = QVBoxLayout(browser_group)
        
        # Browser selection
        browser_select_layout = QHBoxLayout()
        browser_select_layout.addWidget(QLabel("Browser:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Firefox", "Chromium"])
        browser_select_layout.addWidget(self.browser_combo)
        
        launch_btn = QPushButton("🚀 Launch Browser")
        launch_btn.clicked.connect(self.launch_browser)
        browser_select_layout.addWidget(launch_btn)
        
        browser_layout.addLayout(browser_select_layout)
        
        # Browser status
        self.browser_status = QLabel("Browser: Not running")
        browser_layout.addWidget(self.browser_status)
        
        layout.addWidget(browser_group)
        
        # DevTools import
        import_group = QGroupBox("DevTools Import")
        import_layout = QVBoxLayout(import_group)
        
        import_btn = QPushButton("📋 Import from Clipboard")
        import_btn.clicked.connect(self.import_from_clipboard)
        import_layout.addWidget(import_btn)
        
        layout.addWidget(import_group)
        
        layout.addStretch()
        return widget
    
    def create_sessions_tab(self):
        """Create session manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Session list
        session_group = QGroupBox("Active Sessions")
        session_layout = QVBoxLayout(session_group)
        
        self.sessions_tree = QTreeWidget()
        self.sessions_tree.setHeaderLabels(["Session ID", "Created", "Status"])
        session_layout.addWidget(self.sessions_tree)
        
        # Session controls
        session_controls = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_sessions)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_session)
        
        session_controls.addWidget(refresh_btn)
        session_controls.addWidget(delete_btn)
        session_controls.addStretch()
        
        session_layout.addLayout(session_controls)
        layout.addWidget(session_group)
        
        return widget
    
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.config.get('gui', {}).get('theme', 'Dark'))
        theme_layout.addWidget(self.theme_combo)
        general_layout.addLayout(theme_layout)
        
        layout.addWidget(general_group)
        
        # API settings
        api_group = QGroupBox("API Settings")
        api_layout = QVBoxLayout(api_group)
        
        # Timeout setting
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self.timeout_edit = QLineEdit(str(self.config.get('api_detection', {}).get('timeout', 30)))
        timeout_layout.addWidget(self.timeout_edit)
        api_layout.addLayout(timeout_layout)
        
        layout.addWidget(api_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("QPushButton { background: #98c379; color: black; font-weight: bold; }")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        return widget
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Project', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        open_action = QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        
        # Base colors
        dark_palette.setColor(QPalette.Window, QColor(40, 44, 52))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 39, 46))
        dark_palette.setColor(QPalette.AlternateBase, QColor(40, 44, 52))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(40, 44, 52))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(62, 68, 81))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(97, 175, 239))
        dark_palette.setColor(QPalette.Highlight, QColor(97, 175, 239))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        QApplication.setPalette(dark_palette)
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: #282c34;
                color: #abb2bf;
            }
            QGroupBox {
                font-weight: bold;
                color: #61afef;
                border: 1px solid #3e4451;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #61afef;
            }
            QPushButton {
                background: #3e4451;
                color: #abb2bf;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #56b6c2;
                color: #282c34;
            }
            QLineEdit, QTextEdit {
                background: #353b45;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox {
                background: #353b45;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 5px;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Scanner thread connections will be setup when thread is created
        pass
    
    # Navigation methods
    def show_dashboard(self):
        self.tab_widget.setCurrentIndex(0)
    
    def show_api_scanner(self):
        self.tab_widget.setCurrentIndex(1)
    
    def show_login_manager(self):
        self.tab_widget.setCurrentIndex(2)
    
    def show_code_generator(self):
        self.tab_widget.setCurrentIndex(3)
    
    def show_browser_integration(self):
        self.tab_widget.setCurrentIndex(4)
    
    def show_session_manager(self):
        self.tab_widget.setCurrentIndex(5)
    
    def show_settings(self):
        self.tab_widget.setCurrentIndex(6)
    
    # Functional methods
    def browse_file(self):
        """Browse for DevTools log file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DevTools Log", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.devtools_input.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read file: {e}")
    
    def clear_input(self):
        """Clear input fields"""
        self.devtools_input.clear()
        self.file_path_edit.clear()
    
    def start_scan(self):
        """Start API scanning"""
        devtools_data = self.devtools_input.toPlainText().strip()
        
        if not devtools_data:
            QMessageBox.warning(self, "Warning", "Please enter DevTools data or select a file.")
            return
        
        # Disable UI during scan
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start scanner thread
        self.scanner_thread = ScannerThread(devtools_data, self.config)
        self.scanner_thread.progress_signal.connect(self.update_progress)
        self.scanner_thread.finished_signal.connect(self.scan_completed)
        self.scanner_thread.error_signal.connect(self.scan_error)
        self.scanner_thread.start()
        
        self.status_bar.showMessage("Scanning APIs...")
    
    def update_progress(self, value, message):
        """Update progress bar and label"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def scan_completed(self, results):
        """Handle scan completion"""
        self.api_results = results
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Display results in table
        self.display_results(results)
        
        # Update activity log
        self.add_activity(f"API scan completed: {len(results)} APIs found")
        
        self.status_bar.showMessage(f"Scan completed: {len(results)} APIs found")
        
        # Show success message
        successful = sum(1 for r in results if r.get('success', False))
        QMessageBox.information(self, "Scan Complete", 
                              f"Found {len(results)} APIs\n"
                              f"Successful: {successful}\n"
                              f"Failed: {len(results) - successful}")
    
    def scan_error(self, error_message):
        """Handle scan errors"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n{error_message}")
        self.status_bar.showMessage("Scan failed")
    
    def display_results(self, results):
        """Display results in table"""
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # API URL
            url_item = QTableWidgetItem(result.get('api', 'Unknown'))
            self.results_table.setItem(row, 0, url_item)
            
            # Status
            status = "✅" if result.get('success', False) else "❌"
            status_item = QTableWidgetItem(status)
            self.results_table.setItem(row, 1, status_item)
            
            # Type
            type_item = QTableWidgetItem(result.get('type', 'UNKNOWN'))
            self.results_table.setItem(row, 2, type_item)
            
            # Method
            method_item = QTableWidgetItem(result.get('method', 'GET'))
            self.results_table.setItem(row, 3, method_item)
            
            # Response preview
            response = result.get('response', '')
            preview = response[:100] + "..." if len(response) > 100 else response
            response_item = QTableWidgetItem(preview)
            self.results_table.setItem(row, 4, response_item)
    
    def handle_login(self):
        """Handle login attempt"""
        url = self.login_url_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not url or not username or not password:
            QMessageBox.warning(self, "Warning", "Please fill all login fields.")
            return
        
        try:
            login_handler = LoginHandler(self.config)
            credentials = {
                'username': username,
                'password': password,
                'url': url
            }
            
            session = login_handler.login_mode(credentials)
            
            if session:
                self.current_session = session
                session_info = login_handler.get_session_info()
                
                # Display session info
                info_text = f"✅ Logged in successfully!\n\n"
                info_text += f"URL: {url}\n"
                info_text += f"Username: {username}\n"
                info_text += f"Cookies: {len(session_info.get('cookies', {}))}\n"
                info_text += f"Session created: {session_info.get('session_data', {}).get('login_time', 'Unknown')}"
                
                self.session_info.setPlainText(info_text)
                self.add_activity(f"Logged in to {url}")
                self.status_bar.showMessage(f"Logged in to {url}")
            else:
                QMessageBox.warning(self, "Login Failed", "Could not login with provided credentials.")
                self.session_info.setPlainText("❌ Login failed")
                
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login:\n{e}")
    
    def generate_code(self):
        """Generate code from API results"""
        if not self.api_results:
            QMessageBox.warning(self, "Warning", "No API results available. Please run a scan first.")
            return
        
        template_type = self.template_combo.currentText()
        
        try:
            code_generator = CodeGenerator(self.config)
            
            if template_type == "Python Requests":
                code = code_generator.generate_python_code(self.api_results, "requests")
            elif template_type == "Python aiohttp":
                code = code_generator.generate_python_code(self.api_results, "aiohttp")
            elif template_type == "cURL":
                commands = code_generator.generate_curl_commands(self.api_results)
                code = "\n\n".join(commands)
            else:  # Bot Template
                code = code_generator.generate_bot_template(self.api_results)
            
            self.generated_code.setPlainText(code)
            self.add_activity(f"Generated {template_type} code")
            self.status_bar.showMessage(f"Generated {template_type} code")
            
        except Exception as e:
            QMessageBox.critical(self, "Code Generation Error", f"An error occurred:\n{e}")
    
    def export_code(self):
        """Export generated code to file"""
        code = self.generated_code.toPlainText().strip()
        
        if not code:
            QMessageBox.warning(self, "Warning", "No code to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Code", "", "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                QMessageBox.information(self, "Export Successful", f"Code exported to:\n{file_path}")
                self.add_activity(f"Exported code to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Could not export code:\n{e}")
    
    def launch_browser(self):
        """Launch integrated browser"""
        browser = self.browser_combo.currentText().lower()
        
        try:
            from integration.browser_launcher import BrowserLauncher
            launcher = BrowserLauncher(self.config)
            
            if browser == "firefox":
                success = launcher.launch_firefox()
            else:
                success = launcher.launch_chromium()
            
            if success:
                self.browser_status.setText(f"Browser: {browser.capitalize()} launched")
                self.add_activity(f"Launched {browser} browser")
            else:
                self.browser_status.setText(f"Browser: Failed to launch {browser}")
                QMessageBox.warning(self, "Browser Error", f"Could not launch {browser} browser")
                
        except Exception as e:
            QMessageBox.critical(self, "Browser Error", f"An error occurred:\n{e}")
    
    def import_from_clipboard(self):
        """Import DevTools data from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if text:
            self.devtools_input.setPlainText(text)
            self.tab_widget.setCurrentIndex(1)  # Switch to scanner tab
            self.status_bar.showMessage("Data imported from clipboard")
        else:
            QMessageBox.information(self, "Clipboard", "Clipboard is empty or contains no text.")
    
    def refresh_sessions(self):
        """Refresh session list"""
        # Placeholder for session refresh
        self.sessions_tree.clear()
        # TODO: Implement session loading
    
    def delete_session(self):
        """Delete selected session"""
        current_item = self.sessions_tree.currentItem()
        if current_item:
            session_id = current_item.text(0)
            # TODO: Implement session deletion
            self.add_activity(f"Deleted session: {session_id}")
    
    def save_settings(self):
        """Save application settings"""
        try:
            # Update config with new values
            self.config['gui']['theme'] = self.theme_combo.currentText().lower()
            self.config['api_detection']['timeout'] = int(self.timeout_edit.text())
            
            # Save config
            config_manager = ConfigManager()
            config_manager.save_config(self.config)
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            self.add_activity("Settings updated")
            
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Could not save settings:\n{e}")
    
    def add_activity(self, message):
        """Add message to activity log"""
        timestamp = QApplication.instance().applicationName()  # Placeholder for timestamp
        current_text = self.activity_log.toPlainText()
        new_text = f"[{timestamp}] {message}\n{current_text}"
        self.activity_log.setPlainText(new_text[:1000])  # Limit to 1000 chars
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Universal API Tester</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Automated API Detection, Testing, and Bot Code Generation Tool</p>
        <p><b>Author:</b> Md Abu Bakkar</p>
        <p><b>GitHub:</b> <a href="https://github.com/Md-Abu-Bakkar/Universal-API-Testing">Md-Abu-Bakkar/Universal-API-Testing</a></p>
        <p>This tool helps developers automatically detect, test, and generate code for web APIs.</p>
        """
        
        QMessageBox.about(self, "About Universal API Tester", about_text)
    
    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Cleanup resources
            if hasattr(self, 'scanner_thread') and self.scanner_thread.isRunning():
                self.scanner_thread.terminate()
                self.scanner_thread.wait()
            
            event.accept()
        else:
            event.ignore()

def main():
    """Main function to run the dashboard"""
    app = QApplication(sys.argv)
    app.setApplicationName("Universal API Tester")
    app.setApplicationVersion("1.0.0")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Create and show dashboard
    dashboard = Dashboard(config)
    dashboard.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
