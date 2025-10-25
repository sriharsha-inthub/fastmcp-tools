"""
Constants and configuration for MuleSoft Assistant.
This file contains all the URLs and configuration values used by the MuleSoft scraper.
"""

# Configuration section for all URLs used in web scraping
# This makes it easier for developers to see where the assistant is getting information from
MULESOFT_URLS = {
    "lts_edge_release_cadence": "https://docs.mulesoft.com/release-notes/mule-runtime/lts-edge-release-cadence",
    "java_support": "https://docs.mulesoft.com/general/java-support",
    "dataweave": "https://docs.mulesoft.com/dataweave/",
    "connectors": "https://docs.mulesoft.com/connectors/",
    "connector_release_notes": "https://docs.mulesoft.com/connectors/introduction/connector-release-notes",
    "dataweave_release_notes_template": "https://docs.mulesoft.com/release-notes/dataweave/dataweave-{version}-release-notes"
}

# Default headers for HTTP requests to avoid being blocked by servers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}