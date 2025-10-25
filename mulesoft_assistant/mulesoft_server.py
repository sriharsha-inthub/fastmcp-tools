"""
MCP MuleSoft Server Module
This module provides tools to scrape MuleSoft documentation for runtime, DataWeave, and connector version information.
"""

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
import requests, re, sys, os
from bs4 import BeautifulSoup
from typing import Dict, List
from pydantic import Field


# Add the current directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now we can use absolute imports
from mulesoft_constants import MULESOFT_URLS
from mulesoft_utils import parse_jdk_versions, is_version_string, extract_version_number
from http_client import get_html_content


# Initialize the FastMCP server
mcp = FastMCP(
    name="MulesoftAssistantServer",
    instructions="""
        This server provides Mulesoft Runtime, Java and Connector Version data. 
        It scrapes official MuleSoft documentation website 
        <https://docs.mulesoft.com> to extract runtime, java and connector 
        versions and compatability information.
        """,
    version="1.0.0",
    auth=None,
    tools=[])

# ============================================================================
# MCP tools for MuleSoft version scraping
# ============================================================================

@mcp.tool(name="get_mulesoft_runtime_versions", tags=["mulesoft", "runtime", "versions", "scraper"], enabled=True)
def get_mulesoft_runtime_versions() -> Dict:
    """
    Scrape MuleSoft documentation to extract ALL EDGE and LTS runtime versions with JDK compatibility.
    Returns comprehensive information about all available MuleSoft runtime versions including:
    - All Edge versions with release dates and JDK compatibility
    - All LTS versions with release dates and JDK compatibility
    - Complete Java compatibility matrix for all versions
    
    Returns:
        Dict: A comprehensive dictionary containing all EDGE and LTS versions with their JDK compatibility information.
    """
    print("get_mulesoft_runtime_versions::tool called.")
    return _scrape_mulesoft_versions()

@mcp.tool(name="get_latest_mulesoft_versions", tags=["mulesoft", "runtime", "latest", "versions"], enabled=True)
def get_latest_mulesoft_versions() -> Dict:
    """
    Get ONLY the latest EDGE and LTS MuleSoft runtime versions with JDK compatibility.
    Returns simplified information focusing only on the most recent MuleSoft runtime versions:
    - Latest Edge version with release date and JDK compatibility
    - Latest LTS version with release date and JDK compatibility
    - Java compatibility matrix for only the latest versions (not all versions)
    
    Returns:
        Dict: A simplified dictionary containing only the latest EDGE and LTS versions.
    """
    print("get_latest_mulesoft_versions::tool called.")
    
    full_info = _scrape_mulesoft_versions()
    
    if "error" in full_info:
        return full_info
    
    # Get the latest versions (first in the list as they are typically ordered by recency)
    latest_edge = full_info["edge_versions"][0] if full_info["edge_versions"] else None
    latest_lts = full_info["lts_versions"][0] if full_info["lts_versions"] else None
    
    # Create java compatibility only for the latest versions
    latest_java_compatibility = {}
    if latest_edge:
        version_key = latest_edge["version"]
        if version_key in full_info["java_compatibility"]:
            latest_java_compatibility[version_key] = full_info["java_compatibility"][version_key]
    if latest_lts:
        version_key = latest_lts["version"]
        if version_key in full_info["java_compatibility"]:
            latest_java_compatibility[version_key] = full_info["java_compatibility"][version_key]
    
    return {
        "latest_edge": latest_edge,
        "latest_lts": latest_lts,
        "java_compatibility": latest_java_compatibility
    }

@mcp.tool(name="get_dataweave_versions", tags=["mulesoft", "dataweave", "versions", "compatibility"], enabled=True)
def get_dataweave_versions() -> Dict:
    """
    Scrape MuleSoft documentation to extract recent DataWeave version compatibility with Mule runtime.
    Returns focused information about recent DataWeave versions and their compatibility with Mule runtime versions:
    - Recent DataWeave version to Mule runtime version mapping (last 1-2 years)
    - Supported JDK versions for each combination
    - Release notes and breaking changes for the most recent versions
    
    Returns:
        Dict: A dictionary containing recent DataWeave version compatibility information with release notes.
    """
    print("get_dataweave_versions::tool called.")
    
    # URLs for scraping - now configurable
    dataweave_url = MULESOFT_URLS["dataweave"]
    java_support_url = MULESOFT_URLS["java_support"]
    
    try:
        # Get DataWeave compatibility information
        dataweave_soup = get_html_content(dataweave_url)
        
        # Get Java support information
        java_soup = get_html_content(java_support_url)
        
        # Extract version information
        versions_info = _extract_dataweave_versions(dataweave_soup, java_soup)
        
        return versions_info
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch MuleSoft documentation: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to parse MuleSoft documentation: {str(e)}"}

@mcp.tool(name="get_connector_versions", tags=["mulesoft", "connectors", "versions", "compatibility"], enabled=True)
def get_connector_versions(artifactId: str = None) -> Dict:
    """
    Scrape MuleSoft documentation to extract Anypoint Connector version compatibility.
    Returns information about connector versions and their compatibility with Mule runtime versions:
    - Latest connector versions
    - Mule runtime compatibility for each connector
    - JDK compatibility information
    
    Args:
        artifactId (str, optional): Specific connector artifact ID to get version information for.
            If not provided, returns general connector compatibility information.
            Examples: http, salesforce, snowflake, email, sockets
    
    Returns:
        Dict: A dictionary containing connector version compatibility information.
    """
    print(f"get_connector_versions::tool called with artifactId: {artifactId}")
    
    # URLs for scraping - now configurable
    connectors_url = MULESOFT_URLS["connectors"]
    java_support_url = MULESOFT_URLS["java_support"]
    
    try:
        # Get connector information
        connectors_soup = get_html_content(connectors_url)
        
        # Get Java support information
        java_soup = get_html_content(java_support_url)
        
        # Extract version information
        versions_info = _extract_connector_versions(connectors_soup, java_soup, artifactId)
        
        return versions_info
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch MuleSoft documentation: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to parse MuleSoft documentation: {str(e)}"}


def _scrape_mulesoft_versions() -> Dict:
    """
    Core function to scrape MuleSoft documentation for runtime versions.
    
    Returns:
        Dict: A dictionary containing EDGE and LTS versions with their JDK compatibility information.
    """
    # URLs for scraping - now configurable
    lts_edge_url = MULESOFT_URLS["lts_edge_release_cadence"]
    java_support_url = MULESOFT_URLS["java_support"]
    
    try:
        # Get EDGE and LTS information
        lts_edge_soup = get_html_content(lts_edge_url)
        
        # Get Java support information
        java_soup = get_html_content(java_support_url)
        
        # Extract version information from tables
        versions_info = _extract_versions_from_tables(lts_edge_soup, java_soup)
        
        return versions_info
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch MuleSoft documentation: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to parse MuleSoft documentation: {str(e)}"}

def _extract_versions_from_tables(lts_edge_soup, java_soup) -> Dict:
    """
    Extract version information from the documentation tables.
    
    Args:
        lts_edge_soup: BeautifulSoup object for LTS/Edge page
        java_soup: BeautifulSoup object for Java support page
        
    Returns:
        Dict: Structured version information
    """
    # Find tables in the LTS/Edge page
    tables = lts_edge_soup.find_all('table')
    
    # Find the main version table (usually the first large table with version data)
    version_data = []
    edge_versions = []
    lts_versions = []
    
    # Look for the table with version information (skip header tables)
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:  # Make sure it's not just a header
            # Check if this table contains version data by looking for version patterns
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td'])
                if len(cells) >= 3:
                    version_text = cells[0].get_text(strip=True)
                    # Check if this looks like a version entry (contains numbers and Edge/LTS)
                    if is_version_string(version_text):
                        jdk_string = cells[2].get_text(strip=True)
                        jdk_array = parse_jdk_versions(jdk_string)
                        
                        version_data.append({
                            'version': version_text,
                            'release_date': cells[1].get_text(strip=True),
                            'jdk_versions': jdk_array,
                            'jdk_versions_string': jdk_string,  # Keep original string for reference
                            'type': 'Edge' if 'Edge' in version_text else 'LTS' if 'LTS' in version_text else 'Unknown'
                        })
                        # Categorize as Edge or LTS
                        if 'Edge' in version_text:
                            edge_versions.append({
                                'version': version_text,
                                'release_date': cells[1].get_text(strip=True),
                                'jdk_versions': jdk_array
                            })
                        elif 'LTS' in version_text:
                            lts_versions.append({
                                'version': version_text,
                                'release_date': cells[1].get_text(strip=True),
                                'jdk_versions': jdk_array
                            })
    
    # If we couldn't categorize properly, try a different approach
    if not edge_versions and not lts_versions and version_data:
        # Assume first few entries are Edge, last one is LTS (based on typical ordering)
        for item in version_data[:3]:  # First 3 as Edge
            edge_versions.append(item)
        if version_data:
            lts_versions.append(version_data[-1])  # Last one as LTS
    
    # Extract Java support information
    java_tables = java_soup.find_all('table')
    java_data = {}
    java_data_strings = {}
    if java_tables:
        # Look for the table with Java compatibility data
        for table in java_tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td'])
                    if len(cells) >= 2:
                        version = cells[0].get_text(strip=True)
                        jdk_support = cells[1].get_text(strip=True)
                        # Only add if it looks like a version entry
                        if is_version_string(version):
                            java_data[version] = parse_jdk_versions(jdk_support)
                            java_data_strings[version] = jdk_support  # Keep original string
    
    return {
        "edge_versions": edge_versions,
        "lts_versions": lts_versions,
        "java_compatibility": java_data,
        "java_compatibility_strings": java_data_strings,
        "source_urls": [
            MULESOFT_URLS["lts_edge_release_cadence"],
            MULESOFT_URLS["java_support"]
        ]
    }

def _extract_connector_versions(connectors_soup, java_soup, artifactId=None) -> Dict:
    """
    Extract connector version information from the documentation.
    
    Args:
        connectors_soup: BeautifulSoup object for Connectors page
        java_soup: BeautifulSoup object for Java support page
        artifactId (str, optional): Specific connector artifact ID to get version information for
        
    Returns:
        Dict: Structured version information
    """
    # Extract Java support information
    java_tables = java_soup.find_all('table')
    java_data = {}
    if java_tables:
        # Look for the table with Java compatibility data
        for table in java_tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td'])
                    if len(cells) >= 2:
                        version = cells[0].get_text(strip=True)
                        jdk_support = cells[1].get_text(strip=True)
                        # Only add if it looks like a version entry
                        if is_version_string(version):
                            # Parse JDK versions to array
                            java_data[version] = parse_jdk_versions(jdk_support)
    
    # If artifactId is provided, try to get specific connector information
    if artifactId:
        # First, let's find the actual connector link from the release notes page
        release_notes_url = MULESOFT_URLS["connector_release_notes"]
        try:
            release_notes_soup = get_html_content(release_notes_url)
            
            # Look for the connector link in the release notes page
            connector_link = None
            connector_name = None
            
            # Try different variations of the connector name to match what's in the docs
            # The docs often have patterns like "HTTP Connector Release Notes" or "Salesforce Connector Release Notes"
            variations = [
                artifactId.lower(),  # Exact match lowercase
                f"{artifactId.lower()} connector",  # With "connector" suffix lowercase
                f"{artifactId.lower()} connector release notes",  # Full pattern lowercase
                artifactId,  # Exact match
                f"{artifactId} Connector",  # With "Connector" suffix
                f"{artifactId} Connector Release Notes",  # Full pattern
                f"{artifactId.upper()} Connector Release Notes",  # Uppercase version
                f"{artifactId.capitalize()} Connector Release Notes",  # Capitalized version
            ]
            
            # Look for links in the release notes page
            for link in release_notes_soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                href = link['href']
                
                # Check if any of our variations match the link text
                for variation in variations:
                    if variation.lower() in link_text or variation.lower() == link_text.replace(" release notes", "").strip():
                        connector_link = href
                        connector_name = link.get_text(strip=True)
                        # Extract the actual connector name (without "Release Notes")
                        if " Release Notes" in connector_name:
                            actual_connector_name = connector_name.replace(" Release Notes", "")
                        else:
                            actual_connector_name = connector_name
                        print(f"Found connector link: {connector_name} -> {connector_link}")
                        break
                
                if connector_link:
                    break
            
            # If we found a connector link, try to access it
            if connector_link:
                # Convert relative link to absolute URL
                if connector_link.startswith('../../'):
                    # For ../../release-notes/connector/ links, the correct path is /release-notes/connector/
                    if '/release-notes/connector/' in connector_link:
                        connector_url = "https://docs.mulesoft.com" + connector_link[5:]  # Remove ../..
                    else:
                        connector_url = MULESOFT_URLS["connectors"] + connector_link[6:]  # Remove ../../
                elif connector_link.startswith('../'):
                    connector_url = MULESOFT_URLS["connectors"] + "introduction/" + connector_link[3:]  # Remove ../
                elif connector_link.startswith('/'):
                    connector_url = "https://docs.mulesoft.com" + connector_link
                elif connector_link.startswith('http'):
                    # Already an absolute URL
                    connector_url = connector_link
                else:
                    connector_url = MULESOFT_URLS["connectors"] + "introduction/" + connector_link
                
                print(f"Accessing connector URL: {connector_url}")
                
                try:
                    connector_soup = get_html_content(connector_url)
                    
                    # Better approach: Find all compatibility tables first, then associate them with versions
                    # Find all tables with 'Software' and 'Version' headers
                    compatibility_tables = []
                    tables = connector_soup.find_all('table')
                    
                    for i, table in enumerate(tables):
                        rows = table.find_all('tr')
                        if len(rows) >= 2:
                            # Check if this is a compatibility table
                            header_cells = rows[0].find_all(['th', 'td'])
                            header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
                            if 'software' in header_texts and 'version' in header_texts:
                                # Extract compatibility information
                                mule_version = "Unknown"
                                jdk_versions = []
                                
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td'])
                                    if len(cells) >= 2:
                                        software = cells[0].get_text(strip=True)
                                        version_info = cells[1].get_text(strip=True)
                                        if software == 'Mule':
                                            mule_version = version_info
                                        elif 'OpenJDK' in software or 'JDK' in software:
                                            jdk_versions = parse_jdk_versions(version_info)
                                
                                compatibility_tables.append({
                                    'table_index': i,
                                    'table_element': table,
                                    'mule_version': mule_version,
                                    'jdk_versions': jdk_versions
                                })
                    
                    # Look for version headings in the release notes (h2, h3, h4)
                    headings = connector_soup.find_all(['h2', 'h3', 'h4'])
                    version_pattern = re.compile(r'.*(?:[Vv]ersion\s*)?[\d]+\.[\d]+(?:\.[\d]+)?.*')
                    
                    connector_versions = []
                    
                    # Find the most common compatibility information to use as default
                    default_mule_version = "Unknown"
                    default_jdk_versions = []
                    
                    if compatibility_tables:
                        # Use the first compatibility table as the default (they're usually the same)
                        default_mule_version = compatibility_tables[0]['mule_version']
                        default_jdk_versions = compatibility_tables[0]['jdk_versions']
                    
                    for heading in headings:
                        text = heading.get_text(strip=True)
                        if version_pattern.match(text):
                            # Extract the version number
                            connector_version = extract_version_number(text)
                            
                            # Use the default compatibility information for all versions
                            # In most cases, all versions of a connector have the same compatibility
                            mule_version = default_mule_version
                            jdk_versions = default_jdk_versions
                            
                            # Determine the Maven artifactId based on the connector
                            maven_artifact_id = f"mule-{artifactId}-connector"
                            if artifactId == "http":
                                maven_artifact_id = "mule-http-connector"
                            elif artifactId == "email":
                                maven_artifact_id = "mule-email-connector"
                            elif artifactId == "sockets":
                                maven_artifact_id = "mule-sockets-connector"
                            
                            connector_versions.append({
                                'connector_version': connector_version,
                                'mule_version': mule_version,
                                'jdk_versions': jdk_versions,
                                'artifactId': artifactId,
                                'maven_artifact_id': maven_artifact_id,
                                'connector_name': actual_connector_name if 'actual_connector_name' in locals() else connector_name
                            })
                    
                    # If we found specific connector versions, return them
                    if connector_versions:
                        return {
                            "connector_specific": connector_versions,
                            "java_compatibility": java_data,
                            "source_urls": [
                                connector_url,
                                MULESOFT_URLS["java_support"]
                            ]
                        }
                    else:
                        # If no specific versions found, try a different approach
                        # Look for any version-like patterns in the page
                        all_text = connector_soup.get_text()
                        version_matches = re.findall(r'(?:[Vv]ersion\s*)?[\d]+\.[\d]+(?:\.[\d]+)?', all_text)
                        if version_matches:
                            # Just return the first few versions found
                            simple_versions = []
                            for i, version in enumerate(version_matches[:5]):  # Limit to first 5
                                # Determine the Maven artifactId based on the connector
                                maven_artifact_id = f"mule-{artifactId}-connector"
                                if artifactId == "http":
                                    maven_artifact_id = "mule-http-connector"
                                elif artifactId == "email":
                                    maven_artifact_id = "mule-email-connector"
                                elif artifactId == "sockets":
                                    maven_artifact_id = "mule-sockets-connector"
                                
                                simple_versions.append({
                                    'connector_version': extract_version_number(version),
                                    'mule_version': "Unknown",
                                    'jdk_versions': [],
                                    'artifactId': artifactId,
                                    'maven_artifact_id': maven_artifact_id,
                                    'connector_name': actual_connector_name if 'actual_connector_name' in locals() else connector_name
                                })
                            return {
                                "connector_specific": simple_versions,
                                "java_compatibility": java_data,
                                "source_urls": [
                                    connector_url,
                                    MULESOFT_URLS["java_support"]
                                ]
                            }
                        else:
                            # If no specific versions found, return a message indicating that
                            return {
                                "message": f"Connector '{artifactId}' found at {connector_url}, but specific version compatibility information could not be extracted. Please check the connector documentation directly.",
                                "artifactId": artifactId,
                                "connector_url": connector_url,
                                "connector_name": actual_connector_name if 'actual_connector_name' in locals() else connector_name,
                                "java_compatibility": java_data,
                                "source_urls": [
                                    connector_url,
                                    MULESOFT_URLS["java_support"]
                                ]
                            }
                except Exception as e:
                    # If there's an error fetching the connector page, return error info
                    return {
                        "error": f"Could not fetch connector page for '{artifactId}' at {connector_url}: {str(e)}",
                        "artifactId": artifactId,
                        "connector_url": connector_url,
                        "connector_name": actual_connector_name if 'actual_connector_name' in locals() else connector_name
                    }
            else:
                # Connector not found in release notes
                return {
                    "error": f"Connector '{artifactId}' not found in the release notes. Please check the artifactId and try again.",
                    "artifactId": artifactId,
                    "attempted_variations": variations
                }
        except Exception as e:
            # Error accessing release notes
            return {
                "error": f"Could not access connector release notes page: {str(e)}",
                "artifactId": artifactId
            }
    
    # Get general connector information (fallback or when no specific artifactId provided)
    connector_info = []
    # This would normally parse specific connector compatibility but for now
    # we'll provide the general Mule runtime compatibility matrix
    for mule_version, jdk_versions in java_data.items():
        connector_info.append({
            'mule_version': mule_version,
            'jdk_versions': jdk_versions,
            'note': 'General Mule runtime compatibility - check individual connector release notes for specific connector compatibility'
        })
    
    return {
        "connector_compatibility": connector_info,
        "java_compatibility": java_data,
        "source_urls": [
            MULESOFT_URLS["connectors"],
            MULESOFT_URLS["java_support"]
        ]
    }

def _extract_dataweave_versions(dataweave_soup, java_soup) -> Dict:
    """
    Extract DataWeave version information from the documentation.
    
    Args:
        dataweave_soup: BeautifulSoup object for DataWeave page
        java_soup: BeautifulSoup object for Java support page
        
    Returns:
        Dict: Structured version information
    """
    # Find the compatibility table in the DataWeave page
    tables = dataweave_soup.find_all('table')
    
    # Look for the compatibility table
    compatibility_data = []
    if tables:
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                # Check if this looks like a compatibility table by looking for version patterns
                header_row = rows[0]
                header_cells = header_row.find_all(['th', 'td'])
                header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
                
                # Check if this is a compatibility table (has mule/runtime in headers)
                if any('mule' in text or 'runtime' in text for text in header_texts):
                    # Extract data rows
                    for row in rows[1:]:
                        cells = row.find_all(['td'])
                        if len(cells) >= 2:
                            mule_version = cells[0].get_text(strip=True)
                            dataweave_version = cells[1].get_text(strip=True)
                            # Check if these look like version numbers
                            if is_version_string(mule_version) and is_version_string(dataweave_version):
                                compatibility_data.append({
                                    'mule_version': mule_version,
                                    'dataweave_version': dataweave_version
                                })
    
    # Extract Java support information
    java_tables = java_soup.find_all('table')
    java_data = {}
    if java_tables:
        # Look for the table with Java compatibility data
        for table in java_tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td'])
                    if len(cells) >= 2:
                        version = cells[0].get_text(strip=True)
                        jdk_support = cells[1].get_text(strip=True)
                        # Only add if it looks like a version entry
                        if is_version_string(version):
                            # Parse JDK versions to array
                            java_data[version] = parse_jdk_versions(jdk_support)
    
    # Combine the information and filter for recent versions (last 1-2 years)
    combined_data = []
    recent_versions = []  # Focus on the most recent versions
    
    # Sort compatibility data by version (newest first)
    sorted_data = sorted(compatibility_data, 
                        key=lambda x: [int(v) for v in x['mule_version'].split('.')] if '.' in x['mule_version'] else [0], 
                        reverse=True)
    
    # Get the most recent versions (last 1-2 years of releases)
    for item in sorted_data:
        mule_ver = item['mule_version']
        dw_ver = item['dataweave_version']
        
        # Try to find matching JDK versions - look for exact match or match with Edge/LTS suffixes
        jdk_versions = []
        if mule_ver in java_data:
            jdk_versions = java_data[mule_ver]
        else:
            # Check for versions with Edge/LTS suffixes
            for key, value in java_data.items():
                if key.startswith(mule_ver):
                    jdk_versions = value
                    break
        
        # Add to combined data
        combined_data.append({
            'mule_version': mule_ver,
            'dataweave_version': dw_ver,
            'jdk_versions': jdk_versions
        })
        
        # Collect recent versions for focused list
        if len(recent_versions) < 5:  # Limit to 5 most recent versions
            recent_versions.append({
                'mule_version': mule_ver,
                'dataweave_version': dw_ver,
                'jdk_versions': jdk_versions
            })
    
    # Try to get release notes and breaking changes for recent versions
    release_notes_info = {}
    try:
        # For the most recent versions, try to get more detailed information
        for item in recent_versions[:3]:  # Focus on top 3 recent versions
            mule_ver = item['mule_version']
            dw_ver = item['dataweave_version']
            
            # Try to get release notes for this DataWeave version
            # Use the full version format (e.g., 2.10.0 instead of just 2.10)
            release_notes_url = MULESOFT_URLS["dataweave_release_notes_template"].format(version=dw_ver)
            try:
                release_soup = get_html_content(release_notes_url, timeout=10)
                
                # Look for breaking changes or important notes
                breaking_changes = []
                important_notes = []
                new_features = []
                
                # Look for sections with breaking changes or important information
                for heading in release_soup.find_all(['h2', 'h3', 'h4']):
                    heading_text = heading.get_text(strip=True).lower()
                    if 'breaking' in heading_text:
                        # Get the content following this heading
                        content = []
                        sibling = heading.find_next_sibling()
                        while sibling and sibling.name not in ['h2', 'h3', 'h4']:
                            if sibling.get_text(strip=True):
                                content.append(sibling.get_text(strip=True))
                            sibling = sibling.find_next_sibling()
                        breaking_changes.extend(content[:2])  # Limit to first 2 breaking changes
                    elif 'what\'s new' in heading_text or 'new features' in heading_text:
                        # Get new features
                        content = []
                        sibling = heading.find_next_sibling()
                        while sibling and sibling.name not in ['h2', 'h3', 'h4']:
                            if sibling.get_text(strip=True):
                                content.append(sibling.get_text(strip=True))
                            sibling = sibling.find_next_sibling()
                        new_features.extend(content[:3])  # Limit to first 3 new features
                    elif 'important' in heading_text or 'upgrade' in heading_text:
                        # Get important notes
                        content = []
                        sibling = heading.find_next_sibling()
                        while sibling and sibling.name not in ['h2', 'h3', 'h4']:
                            if sibling.get_text(strip=True):
                                content.append(sibling.get_text(strip=True))
                            sibling = sibling.find_next_sibling()
                        important_notes.extend(content[:2])  # Limit to first 2 important notes
                
                # If we didn't find specific breaking changes, look for any warnings or cautions
                if not breaking_changes:
                    for p in release_soup.find_all('p'):
                        text = p.get_text(strip=True).lower()
                        if 'warning:' in text or 'caution:' in text or 'deprecated' in text:
                            breaking_changes.append(p.get_text(strip=True))
                
                release_notes_info[dw_ver] = {
                    'breaking_changes': breaking_changes[:3],  # Limit to first 3 breaking changes
                    'new_features': new_features[:5],          # Limit to first 5 new features
                    'important_notes': important_notes[:3],    # Limit to first 3 important notes
                    'release_notes_url': release_notes_url
                }
            except Exception as e:
                # If we can't get release notes, continue without them
                print(f"Could not fetch release notes for DataWeave {dw_ver}: {str(e)}")
                pass
    except Exception as e:
        # If there are any issues getting release notes, continue without them
        print(f"Error getting release notes: {str(e)}")
        pass
    
    return {
        "recent_dataweave_versions": recent_versions,  # Focused list of recent versions
        "all_compatibility_data": combined_data,       # Complete compatibility data
        "release_notes": release_notes_info,           # Release notes and breaking changes for recent versions
        "java_compatibility": java_data,
        "source_urls": [
            MULESOFT_URLS["dataweave"],
            MULESOFT_URLS["java_support"]
        ]
    }

# ============================================================================
# MCP Prompt Server for MuleSoft Assistant
# ============================================================================

@mcp.prompt
def list_all_mulesoft_runtime_versions() -> PromptMessage:
    """
    Retrieves a complete list of MuleSoft EDGE and LTS runtime versions together
    with their JDK compatibility matrix.

    Returns:
        PromptMessage – a user‑role message containing a short description of the
        request. The LLM will then call the underlying tool and return the data.
    """
    content = (
        "Please provide **all** MuleSoft EDGE and LTS runtime versions, "
        "including release dates and the JDK versions each runtime supports."
    )
    return PromptMessage(
        role="user",
        content=TextContent(type="text", text=content)
    )

@mcp.prompt
def show_latest_mulesoft_versions() -> str:
    """
    Retrieves only the most recent MuleSoft EDGE and LTS runtime versions
    together with their JDK compatibility.

    Returns:
        str – a short user‑message; FastMCP will wrap it automatically.
    """
    return (
        "Give me the **latest** MuleSoft EDGE and LTS runtime versions "
        "with their release dates and supported JDK versions."
    )

@mcp.prompt
def recent_dataweave_compatibility() -> PromptMessage:
    """
    Returns recent DataWeave versions and the Mule runtime versions they are
    compatible with, together with the supported JDK versions and any
    release‑note highlights.

    Returns:
        PromptMessage – a user‑role message that explains the desired output.
    """
    content = (
        "List the most recent DataWeave versions, the Mule runtime versions they "
        "work with, and the JDK versions supported. Include any notable release "
        "notes or breaking changes for the last three DataWeave releases."
    )
    return PromptMessage(
        role="user",
        content=TextContent(type="text", text=content)
    )

@mcp.prompt
def list_all_connector_compatibility() -> str:
    """
    Retrieves a matrix of Mule runtime versions and JDK compatibility for **all**
    MuleSoft connectors (no specific artifactId).

    Returns:
        str – a short request that the LLM will forward to the tool.
    """
    return (
        "Provide a compatibility matrix for **all** MuleSoft connectors, "
        "showing which Mule runtime versions and JDK versions each connector supports."
    )

# ============================================================================
# MCP Server Entry Point
# ============================================================================
if __name__ == "__main__":
    # Run as stdio server
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9001, path="/mcp", show_banner=False)