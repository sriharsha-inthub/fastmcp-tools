# 1. Virtual env setup & install pre-requisites

```
echo "Create a virtual environment
python -m venv .venv

echo "Active teh virtual environemnt
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
python fastmcp_calculator.py

echo "In a new terminal; inspect mcp
npx @modelcontextprotocol/inspector python fastmcp_calculator.py

echo "Explore mcp inspector; connect & test resources - tools."
```


## 1.2 Explore & Test -FastAPI-MCP

```
echo "Required packages are fastapi, fastapi-mcp & unicorm (server)"
echo "pip install fastapi fastapi-mcp uvicorn[standard]"
echo "Run mcp server"
python fastapi_mcp_calculator.py

echo "In a new terminal; inspect mcp
npx @modelcontextprotocol/inspector python fastapi_mcp_calculator.py

echo "Explore mcp inspector; connect & test resources - tools."
```

## Generfate mcp-json config.
```
fastmcp install mcp-json --server-spec calculator_http.py --copy
```

## 1.3 MuleSoft Runtime Versions Scraper

```
echo "Run MuleSoft scraper as HTTP server"
python mulesoft_scraper.py

echo "Run MuleSoft scraper as Stdio server"
python mulesoft_scraper_stdio.py

echo "In a new terminal; inspect mcp"
npx @modelcontextprotocol/inspector python mulesoft_scraper.py

echo "Explore mcp inspector; connect & test resources - tools."
```