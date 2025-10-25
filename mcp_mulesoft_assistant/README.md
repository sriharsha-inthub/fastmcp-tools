# MCP MuleSoft Module

This module provides tools to scrape MuleSoft documentation for runtime, DataWeave, and connector version information.

## File Structure

```
mcp_mulesoft_assistant/
├── mcp_mulesoft_server.py     # Main module with scraping tools
├── mulesoft_constants.py      # Configuration and URL constants
├── mulesoft_utils.py          # Utility functions
└── http_client.py             # HTTP client utilities

quickstart/
├── calculator_stdio.py        # Calculator example (stdio)
├── calculator_http.py         # Calculator example (HTTP)
├── calculator_api.py          # Calculator example (API)
├── rssfeed_stdio.py           # RSS feed example (stdio)
└── rssfeed_http.py            # RSS feed example (HTTP)
```

## Module Descriptions

### mcp_mulesoft_server.py
Main module containing all the scraping tools for MuleSoft documentation:
- `get_mulesoft_runtime_versions()` - Get all EDGE and LTS runtime versions
- `get_latest_mulesoft_versions()` - Get only the latest EDGE and LTS versions
- `get_dataweave_versions()` - Get DataWeave version compatibility
- `get_connector_versions()` - Get connector version compatibility

### mulesoft_constants.py
Configuration file containing:
- All URLs used for web scraping
- Default HTTP headers
- Other configuration values

### mulesoft_utils.py
Utility functions used across the module:
- `parse_jdk_versions()` - Parse JDK version strings
- `is_version_string()` - Check if text looks like a version
- `extract_version_number()` - Extract version numbers from text

### http_client.py
HTTP client utilities:
- `make_http_request()` - Make HTTP requests with default headers
- `get_html_content()` - Get parsed HTML content from URLs

## Naming Conventions

### Folders
- Use lowercase with underscores: `mcp_mulesoft_assistant`
- Be descriptive but concise
- Use `mcp_` prefix for MCP tools

### Python Files
- Use lowercase with underscores: `mcp_mulesoft_server.py`
- Be descriptive about the file's purpose
- Include module type when relevant: `_constants.py`, `_utils.py`, `_client.py`
- Use `mcp_` prefix for main server files

### Functions/Variables
- Use snake_case: `get_mulesoft_runtime_versions`
- Be descriptive about purpose
- Use verbs for functions: `get_`, `parse_`, `extract_`

### Constants
- Use UPPER_SNAKE_CASE: `MULESOFT_URLS`
- Define in separate constants files when possible