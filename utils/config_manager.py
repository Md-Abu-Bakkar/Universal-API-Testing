"""
Configuration Manager - Handle application configuration
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Try user config directory first
        if os.name == 'posix':  # Linux, macOS, Termux
            config_dir = os.path.join(os.path.expanduser('~'), '.config', 'universal-api-tester')
        elif os.name == 'nt':  # Windows
            config_dir = os.path.join(os.environ.get('APPDATA', ''), 'UniversalAPITester')
        else:  # Other platforms
            config_dir = os.path.join(os.path.expanduser('~'), '.universal-api-tester')
        
        return os.path.join(config_dir, 'config.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = self._get_default_config()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Merge with default config
                merged_config = self._merge_configs(default_config, user_config)
                logger.info(f"Configuration loaded from {self.config_file}")
                return merged_config
                
            except Exception as e:
                logger.error(f"Error loading config from {self.config_file}: {e}")
                logger.info("Using default configuration")
                return default_config
        else:
            logger.info("No config file found, using default configuration")
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "app": {
                "name": "Universal API Tester",
                "version": "1.0.0",
                "author": "Md Abu Bakkar",
                "description": "Automated API Detection, Testing, and Bot Code Generation Tool"
            },
            "browser": {
                "firefox_path": "/data/data/com.termux/files/usr/bin/firefox",
                "chromium_path": "/data/data/com.termux/files/usr/bin/chromium",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "timeout": 30
            },
            "api_detection": {
                "timeout": 30,
                "retry_attempts": 3,
                "max_apis_per_scan": 50,
                "enable_auto_classification": True,
                "response_size_limit": 1048576
            },
            "login": {
                "max_login_attempts": 3,
                "session_timeout": 3600,
                "auto_captcha_solve": True,
                "save_cookies": True
            },
            "export": {
                "python_template": "requests",
                "include_comments": True,
                "add_headers": True,
                "add_error_handling": True,
                "default_output_dir": "./exports"
            },
            "gui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "auto_save_logs": True,
                "show_line_numbers": True
            },
            "security": {
                "verify_ssl": False,
                "allow_redirects": True,
                "max_redirects": 5,
                "user_agent_rotation": False
            },
            "logging": {
                "level": "INFO",
                "file_path": "./logs/api_tester.log",
                "max_file_size": 10485760,
                "backup_count": 5
            },
            "advanced": {
                "concurrent_requests": 5,
                "delay_between_requests": 1,
                "enable_proxy": False,
                "proxy_url": "",
                "custom_headers": {},
                "blacklist_domains": ["google.com", "facebook.com", "twitter.com"]
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        merged = default.copy()
        
        for key, value in user.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (uses current config if None)
            
        Returns:
            bool: True if successful
        """
        try:
            config_to_save = config or self.config
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            self.config = config_to_save
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config to {self.config_file}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (e.g., "api_detection.timeout")
            default: Default value if key not found
            
        Returns:
            any: Configuration value
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.debug(f"Error getting config key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key (e.g., "api_detection.timeout")
            value: Value to set
            
        Returns:
            bool: True if successful
        """
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the final key
            for k in keys[:-1]:
                if k not in config_ref or not isinstance(config_ref[k], dict):
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set the final key
            config_ref[keys[-1]] = value
            
            # Save the updated configuration
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error setting config key {key}: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
            
        Returns:
            bool: True if all updates successful
        """
        success = True
        
        for key, value in updates.items():
            if not self.set(key, value):
                success = False
        
        return success
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            logger.error(f"Error resetting config to defaults: {e}")
            return False
    
    def get_config_path(self) -> str:
        """Get configuration file path"""
        return self.config_file
    
    def create_backup(self, backup_path: str = None) -> str:
        """
        Create configuration backup
        
        Args:
            backup_path: Backup file path
            
        Returns:
            str: Path to backup file
        """
        try:
            if not backup_path:
                import datetime
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir = os.path.join(os.path.dirname(self.config_file), 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f'config_backup_{timestamp}.json')
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating config backup: {e}")
            raise
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore configuration from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_config = json.load(f)
            
            self.config = backup_config
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error restoring config from backup: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration
        
        Returns:
            dict: Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate required sections
        required_sections = ['api_detection', 'login', 'export', 'security']
        for section in required_sections:
            if section not in self.config:
                results['errors'].append(f"Missing required section: {section}")
                results['valid'] = False
        
        # Validate API detection settings
        api_timeout = self.get('api_detection.timeout')
        if not isinstance(api_timeout, (int, float)) or api_timeout <= 0:
            results['errors'].append("api_detection.timeout must be a positive number")
            results['valid'] = False
        
        # Validate export directory
        export_dir = self.get('export.default_output_dir')
        if export_dir:
            try:
                # Check if directory is writable
                test_file = os.path.join(export_dir, '.write_test')
                os.makedirs(export_dir, exist_ok=True)
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                results['warnings'].append(f"Export directory may not be writable: {e}")
        
        # Validate browser paths if specified
        browsers = ['firefox', 'chromium']
        for browser in browsers:
            path = self.get(f'browser.{browser}_path')
            if path and not os.path.exists(path):
                results['warnings'].append(f"{browser} path not found: {path}")
        
        return results
    
    def export_config_schema(self) -> Dict[str, Any]:
        """Export configuration schema"""
        return {
            "type": "object",
            "properties": {
                "app": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "author": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                "api_detection": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "number", "minimum": 1},
                        "retry_attempts": {"type": "integer", "minimum": 1},
                        "max_apis_per_scan": {"type": "integer", "minimum": 1},
                        "enable_auto_classification": {"type": "boolean"},
                        "response_size_limit": {"type": "integer", "minimum": 0}
                    }
                },
                # Add more schema definitions as needed
            },
            "required": ["app", "api_detection", "login", "export", "security"]
        }
