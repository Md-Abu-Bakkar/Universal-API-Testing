"""
File Exporter - Export data to various formats
"""

import json
import csv
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

class FileExporter:
    """Export data to various file formats"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.default_output_dir = self.config.get('export', {}).get('default_output_dir', './exports')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.default_output_dir, exist_ok=True)
    
    def export_json(self, data: Any, filename: str, output_dir: str = None) -> str:
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            output_dir = output_dir or self.default_output_dir
            filepath = self._get_filepath(filename, 'json', output_dir)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported JSON to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            raise
    
    def export_csv(self, data: List[Dict[str, Any]], filename: str, 
                   output_dir: str = None) -> str:
        """
        Export data to CSV file
        
        Args:
            data: List of dictionaries to export
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            if not data:
                raise ValueError("No data to export")
            
            output_dir = output_dir or self.default_output_dir
            filepath = self._get_filepath(filename, 'csv', output_dir)
            
            # Get all fieldnames from data
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Exported CSV to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise
    
    def export_text(self, data: str, filename: str, output_dir: str = None) -> str:
        """
        Export text data to file
        
        Args:
            data: Text data to export
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            output_dir = output_dir or self.default_output_dir
            filepath = self._get_filepath(filename, 'txt', output_dir)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            logger.info(f"Exported text to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting text: {e}")
            raise
    
    def export_yaml(self, data: Any, filename: str, output_dir: str = None) -> str:
        """
        Export data to YAML file
        
        Args:
            data: Data to export
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            output_dir = output_dir or self.default_output_dir
            filepath = self._get_filepath(filename, 'yaml', output_dir)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Exported YAML to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting YAML: {e}")
            raise
    
    def export_api_results(self, results: List[Dict[str, Any]], 
                          format: str = 'json', filename: str = None,
                          output_dir: str = None) -> str:
        """
        Export API testing results
        
        Args:
            results: API testing results
            format: Export format (json, csv, yaml)
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"api_results_{timestamp}"
            
            if format.lower() == 'json':
                return self.export_json(results, filename, output_dir)
            elif format.lower() == 'csv':
                return self.export_csv(results, filename, output_dir)
            elif format.lower() == 'yaml':
                return self.export_yaml(results, filename, output_dir)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting API results: {e}")
            raise
    
    def export_code(self, code: str, language: str, filename: str = None,
                   output_dir: str = None) -> str:
        """
        Export generated code
        
        Args:
            code: Code to export
            language: Programming language
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"generated_code_{timestamp}"
            
            # Determine file extension based on language
            extensions = {
                'python': 'py',
                'javascript': 'js',
                'typescript': 'ts',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'php': 'php',
                'ruby': 'rb',
                'go': 'go',
                'rust': 'rs',
                'shell': 'sh',
                'curl': 'txt'
            }
            
            extension = extensions.get(language.lower(), 'txt')
            filepath = self._get_filepath(filename, extension, output_dir)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            logger.info(f"Exported {language} code to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting code: {e}")
            raise
    
    def export_config(self, config: Dict[str, Any], filename: str = None,
                     output_dir: str = None) -> str:
        """
        Export configuration
        
        Args:
            config: Configuration data
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"config_{timestamp}"
            
            return self.export_json(config, filename, output_dir)
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            raise
    
    def export_session(self, session_data: Dict[str, Any], filename: str = None,
                      output_dir: str = None) -> str:
        """
        Export session data
        
        Args:
            session_data: Session data
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            str: Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"session_{timestamp}"
            
            return self.export_json(session_data, filename, output_dir)
            
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            raise
    
    def batch_export(self, exports: List[Dict[str, Any]], output_dir: str = None) -> List[str]:
        """
        Perform multiple exports at once
        
        Args:
            exports: List of export configurations
            output_dir: Output directory
            
        Returns:
            list: List of exported file paths
        """
        exported_files = []
        
        for export_config in exports:
            try:
                export_type = export_config.get('type')
                data = export_config.get('data')
                filename = export_config.get('filename')
                format = export_config.get('format', 'json')
                
                if export_type == 'api_results':
                    filepath = self.export_api_results(data, format, filename, output_dir)
                elif export_type == 'code':
                    language = export_config.get('language', 'python')
                    filepath = self.export_code(data, language, filename, output_dir)
                elif export_type == 'config':
                    filepath = self.export_config(data, filename, output_dir)
                elif export_type == 'session':
                    filepath = self.export_session(data, filename, output_dir)
                else:
                    filepath = self.export_json(data, filename, output_dir)
                
                exported_files.append(filepath)
                
            except Exception as e:
                logger.error(f"Error in batch export: {e}")
                continue
        
        return exported_files
    
    def _get_filepath(self, filename: str, extension: str, output_dir: str) -> str:
        """Generate full file path"""
        # Ensure filename has proper extension
        if not filename.endswith(f'.{extension}'):
            filename = f"{filename}.{extension}"
        
        return os.path.join(output_dir, filename)
    
    def list_exports(self, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        List exported files
        
        Args:
            output_dir: Directory to list
            
        Returns:
            list: List of file information
        """
        output_dir = output_dir or self.default_output_dir
        
        if not os.path.exists(output_dir):
            return []
        
        files_info = []
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files_info.append({
                    'name': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': os.path.splitext(filename)[1].lower()
                })
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified'], reverse=True)
        
        return files_info
    
    def cleanup_old_exports(self, max_age_days: int = 30, output_dir: str = None) -> int:
        """
        Clean up old export files
        
        Args:
            max_age_days: Maximum age in days
            output_dir: Directory to clean
            
        Returns:
            int: Number of files deleted
        """
        output_dir = output_dir or self.default_output_dir
        
        if not os.path.exists(output_dir):
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if os.path.isfile(filepath):
                if os.stat(filepath).st_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old export: {filepath}")
                    except Exception as e:
                        logger.error(f"Error deleting {filepath}: {e}")
        
        return deleted_count
