"""
Utility functions for the MuleSoft Assistant.
This file contains shared utility functions used across the MuleSoft assistant modules.
"""

import re
from typing import List

def parse_jdk_versions(jdk_string: str) -> List[int]:
    """
    Convert JDK version string to array of integers.
    
    Args:
        jdk_string (str): String containing JDK versions (e.g., "8, 11, and 17")
        
    Returns:
        List[int]: List of JDK versions as integers
    """
    if not jdk_string:
        return []
    # Handle different formats like "8, 11, and 17" or "8 and 11"
    jdk_string = jdk_string.replace("and", ",").strip()
    # Extract numbers from the string
    numbers = re.findall(r'\d+', jdk_string)
    # Convert to integers
    return [int(num) for num in numbers]

def is_version_string(text: str) -> bool:
    """
    Check if a string looks like a version number.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text looks like a version number
    """
    return bool(re.match(r'^\d+\.\d+', text))

def extract_version_number(text: str) -> str:
    """
    Extract version number from text.
    
    Args:
        text (str): Text containing version information
        
    Returns:
        str: Extracted version number
    """
    version_match = re.search(r'((?:[Vv]ersion\s*)?[\d]+\.[\d]+(?:\.[\d]+)?)', text)
    if version_match:
        return version_match.group(1).replace('Version', '').replace('version', '').strip()
    return ""