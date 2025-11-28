"""
GUI modules for Universal API Tester
"""

from .dashboard import Dashboard
from .browser_integration import BrowserIntegration
from .log_viewer import LogViewer
from .widgets import (ApiResultWidget, CodePreviewWidget, 
                     SessionManagerWidget, ConfigEditorWidget)

__all__ = [
    'Dashboard',
    'BrowserIntegration',
    'LogViewer',
    'ApiResultWidget',
    'CodePreviewWidget',
    'SessionManagerWidget',
    'ConfigEditorWidget'
]
