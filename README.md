# 1. Virtual env setup & install pre-requisites

```
echo "Create a virtual environment"
python -m venv .venv

echo "Activate the virtual environment"
.venv/Scripts/activate.bat

echo "Install all pre-requisites/packages"
pip install -r requirements.txt

echo "Optional - upgrade pip"
python.exe -m pip install --upgrade pip

```

## 1.1 Explore & Test -FastMCP - Stdio ONLY

```
echo "Required package is fastmcp"
echo "pip install fastmcp"

echo "Run mcp server"
python quickstart/calculator_stdio.py

echo "In a new terminal; inspect mcp"
npx @modelcontextprotocol/inspector python quickstart/calculator_stdio.py

echo "Explore mcp inspector; connect & test resources - tools."
```


## 1.2 Explore & Test -FastAPI-MCP

```
echo "Required packages are fastapi, fastapi-mcp & uvicorn (server)"
echo "pip install fastapi fastapi-mcp uvicorn[standard]"
echo "Run mcp server"
python quickstart/calculator_api_http.py

echo "In a new terminal; inspect mcp"
npx @modelcontextprotocol/inspector python quickstart/calculator_api_http.py

echo "Explore mcp inspector; connect & test resources - tools."
```

## Generate mcp-json config.
```
fastmcp install mcp-json --server-spec quickstart/calculator_http.py --copy
```

## 1.3 MuleSoft Runtime Versions Scraper

```
echo "Run MuleSoft scraper as HTTP server"
python quickstart/rssfeed_http.py

echo "Run MuleSoft scraper as Stdio server"
python quickstart/rssfeed_stdio.py

echo "In a new terminal; inspect mcp"
npx @modelcontextprotocol/inspector python quickstart/rssfeed_http.py

echo "Explore mcp inspector; connect & test resources - tools."
```