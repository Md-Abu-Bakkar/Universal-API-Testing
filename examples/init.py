"""
Example files for Universal API Tester
"""

import os
from typing import Dict, Any

def load_example(example_name: str) -> str:
    """
    Load example file by name
    
    Args:
        example_name: Example filename
        
    Returns:
        str: Example content
    """
    example_path = os.path.join(os.path.dirname(__file__), example_name)
    
    try:
        with open(example_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"# Example not found: {example_name}"
    except Exception as e:
        return f"# Error loading example: {str(e)}"

__all__ = ['load_example']
