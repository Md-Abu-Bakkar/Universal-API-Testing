"""
Code templates for Universal API Tester
"""

import os
from typing import Dict, Any

def load_template(template_name: str) -> str:
    """
    Load code template by name
    
    Args:
        template_name: Template filename
        
    Returns:
        str: Template content
    """
    template_path = os.path.join(os.path.dirname(__file__), template_name)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"# Template not found: {template_name}"
    except Exception as e:
        return f"# Error loading template: {str(e)}"

# Available templates
__all__ = ['load_template']
