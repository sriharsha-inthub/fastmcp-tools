# MCP MuleSoft Assistant

The **MCP MuleSoft Assistant** is a lightweight Python package that provides a set of ready‑to‑use tools for scraping MuleSoft documentation.  It can retrieve runtime versions, DataWeave compatibility tables, and connector version information – all without leaving your development environment.

---

## 📦 Installation

The project uses a standard `requirements.txt` file.  From the repository root run the commands that match your operating system.

### Windows

```cmd
python -m venv .venv               # (optional) create an isolated environment
.venv\Scripts\activate             # activate the venv
pip install -r requirements.txt    # install dependencies
```

### Linux / macOS

```bash
python3 -m venv .venv               # (optional) create an isolated environment
source .venv/bin/activate           # activate the venv
pip install -r requirements.txt     # install dependencies
```

If you want to use the assistant as an importable package in other projects you can install it in *editable* mode (works on all platforms):

```bash
pip install -e .
```

---

## 🚀 Usage

All public functions live in `mulesoft_assistant.mulesoft_server`.  A typical workflow looks like this:  
Direct function call(s)  
```python
from mulesoft_assistant import mulesoft_server as mms

# Get every EDGE and LTS runtime version that MuleSoft publishes
all_versions = mms.get_mulesoft_runtime_versions()
print("All runtime versions:", all_versions)

# Get only the latest EDGE and LTS releases
latest = mms.get_latest_mulesoft_versions()
print("Latest runtimes:", latest)

# DataWeave compatibility matrix
dw = mms.get_dataweave_versions()
print("DataWeave versions:", dw)

# Connector version compatibility
connectors = mms.get_connector_versions()
print("Connector versions:", connectors)
```
If you prefer an object‑oriented wrapper, you can create a tiny client class that forwards calls to the server module.  This makes it easy to inject the client into other services or to mock it in tests.

```python
"""Simple client wrapper around the MCP MuleSoft Assistant functions."""

from mulesoft_assistant import mulesoft_server as mms


class MuleSoftAssistantClient:
		"""Encapsulates the public API of the assistant.

		The methods simply delegate to the underlying module functions, but the
		class provides a clear place to add caching, logging, or custom error
		handling in the future.
		"""

		def get_all_runtimes(self):
				return mms.get_mulesoft_runtime_versions()

		def get_latest_runtimes(self):
				return mms.get_latest_mulesoft_versions()

		def get_dataweave_matrix(self):
				return mms.get_dataweave_versions()

		def get_connector_matrix(self):
				return mms.get_connector_versions()


# Example usage
if __name__ == "__main__":
		client = MuleSoftAssistantClient()
		print("All runtimes:", client.get_all_runtimes())
		print("Latest runtimes:", client.get_latest_runtimes())
		print("DataWeave matrix:", client.get_dataweave_matrix())
		print("Connector matrix:", client.get_connector_matrix())
```

### FastMCP Client Integration

You can also interact with the MuleSoft assistant programmatically using the FastMCP client, as described in the [FastMCP documentation](https://gofastmcp.com/getting-started/quickstart#call-your-server):

```python
import asyncio
from fastmcp import Client

# Connect to the assistant running as an HTTP server
client = Client("http://localhost:8000/mcp")

async def get_latest_runtimes():
    async with client:
        # Call the get_latest_mulesoft_versions tool
        result = await client.call_tool("get_latest_mulesoft_versions", {})
        print("Latest runtimes:", result)

asyncio.run(get_latest_runtimes())
```

Note that:
- FastMCP clients are asynchronous, so we use `asyncio.run` to run the client
- We must enter a client context (`async with client:`) before using the client
- You can make multiple client calls within the same context

### Client Integration

The MuleSoft assistant can be easily integrated with various MCP clients using the `fastmcp install` command. Here are the supported integration options:

```bash
fastmcp install --help

Usage: fastmcp install COMMAND
Install MCP servers in various clients and formats.
╭─ Commands ───────────────────────────────────────────────────────────────────────╮
│ claude-code     Install an MCP server in Claude Code.                            │
│ claude-desktop  Install an MCP server in Claude Desktop.                         │
│ cursor          Install an MCP server in Cursor.                                 │
│ gemini-cli      Install an MCP server in Gemini CLI.                             │
│ mcp-json        Generate MCP configuration JSON for manual installation.         │
╰──────────────────────────────────────────────────────────────────────────────────
```

#### Direct Client Integrations

For supported clients, you can directly install the assistant using the specific command:

- **Claude Desktop**: `fastmcp install claude-desktop python mulesoft_assistant\mulesoft_server.py`
- **Claude Code**: `fastmcp install claude-code python mulesoft_assistant\mulesoft_server.py`
- **Cursor**: `fastmcp install cursor python mulesoft_assistant\mulesoft_server.py`
- **Gemini CLI**: `fastmcp install gemini-cli python mulesoft_assistant\mulesoft_server.py`

#### Manual Configuration (mcp-json)

For other MCP-compatible clients or manual setup, use the mcp-json generator:

```bash
fastmcp install mcp-json --server-spec python mulesoft_assistant\mulesoft_server.py --copy
```

This command generates a JSON configuration that can be used with any MCP-compatible client. The `--copy` flag copies the configuration to your clipboard for easy pasting into your client's configuration file.

---

## ✨ Features & Tools

---

## ✨ Features & Tools

| Feature | Description | Primary Function |
|---------|-------------|------------------|
| **Runtime discovery** | Scrapes the MuleSoft runtime download page and extracts both EDGE and LTS versions. | `get_mulesoft_runtime_versions()` |
| **Latest runtime shortcut** | Returns only the most recent EDGE and LTS releases for quick reference. | `get_latest_mulesoft_versions()` |
| **DataWeave compatibility** | Parses the DataWeave version matrix to show which runtime supports which DW version. | `get_dataweave_versions()` |
| **Connector version matrix** | Retrieves connector‑to‑runtime compatibility tables for all official MuleSoft connectors. | `get_connector_versions()` |

### Prompts & MCP Integration

The assistant is designed to be used from **MCP (Model‑Context‑Protocol) tools**.  Example prompts you can feed to an MCP‑enabled LLM:

* "_Give me the latest MuleSoft LTS runtime version._"
* "_Which DataWeave version works with Mule 4.4.0?_"
* "_List all connector versions compatible with Mule 4.5.0 EDGE._"

When these prompts are routed through an MCP tool that calls the corresponding Python function, the LLM receives a structured answer instead of raw scraped HTML.

---

## 📂 File Structure

```
mulesoft_assistant/               # Core package
├── __init__.py                       # Makes the folder a package
├── mulesoft_server.py            # Public API – scraping tools
├── mulesoft_constants.py             # URLs, headers, and static config
├── mulesoft_utils.py                 # Helper utilities (parsing, validation)
└── http_client.py                    # HTTP client utilities

README.md                              # This documentation file
requirements.txt                       # Python dependencies
```

---

## 🛠 Naming Conventions (reminder)

* **Folders** – lower‑case with underscores, prefixed with `mcp_` when they belong to the MCP ecosystem.
* **Python files** – lower‑case with underscores; use a descriptive suffix (`_constants`, `_utils`, `_server`).
* **Functions / variables** – `snake_case`; verbs for actions (`get_`, `parse_`, `extract_`).
* **Constants** – `UPPER_SNAKE_CASE` and kept in dedicated constant modules.

---

## 📄 License

This project is licensed under the MIT License – see the `LICENSE` file for details.
