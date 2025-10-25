"""
HTTP client utilities for the MuleSoft Assistant.
This file contains shared HTTP client functionality used across the MuleSoft assistant modules.
"""

import requests
from typing import Dict, Any, Optional
from .mulesoft_constants import DEFAULT_HEADERS

def make_http_request(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> requests.Response:
    """
    Make an HTTP request with default headers and error handling.
    
    Args:
        url (str): The URL to request
        headers (Dict[str, str], optional): Additional headers to include
        timeout (int): Request timeout in seconds
        
    Returns:
        requests.Response: The HTTP response
        
    Raises:
        requests.RequestException: If the request fails
    """
    # Merge default headers with any provided headers
    request_headers = DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    response = requests.get(url, headers=request_headers, timeout=timeout)
    response.raise_for_status()
    return response

def get_html_content(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Any:
    """
    Get parsed HTML content from a URL.
    
    Args:
        url (str): The URL to request
        headers (Dict[str, str], optional): Additional headers to include
        timeout (int): Request timeout in seconds
        
    Returns:
        BeautifulSoup: Parsed HTML content
        
    Raises:
        requests.RequestException: If the request fails
    """
    from bs4 import BeautifulSoup
    
    response = make_http_request(url, headers, timeout)
    return BeautifulSoup(response.content, 'html.parser')