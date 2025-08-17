# Browser-Use FastAPI Server

This is a FastAPI conversion of the browser-use MCP server, providing the same browser automation capabilities via REST API endpoints.

## Features

The FastAPI server exposes all the browser automation capabilities through REST endpoints:

### Session Management
- `POST /sessions` - Create a new browser session
- `GET /sessions` - List all active sessions
- `DELETE /sessions/{session_id}` - Close a specific session

### Direct Browser Control
- `POST /browser/navigate` - Navigate to a URL
- `POST /browser/click` - Click an element by index
- `POST /browser/type` - Type text into an input field
- `POST /browser/state` - Get current page state with interactive elements
- `POST /browser/extract` - Extract structured content from the page
- `POST /browser/scroll` - Scroll the page
- `POST /browser/back` - Go back in browser history

### Tab Management
- `GET /browser/tabs` - List all open tabs
- `POST /browser/tabs/switch` - Switch to a different tab
- `POST /browser/tabs/close` - Close a specific tab

### Autonomous Agent
- `POST /agent/task` - Run an autonomous browser task
- `GET /agent/task/{task_id}` - Get task status and results

## Installation

Install with API dependencies:

```bash
pip install "browser-use[api]"
```

Or install all dependencies:

```bash
pip install "browser-use[all]"
```

## Usage

### Starting the Server

You can start the server in several ways:

#### 1. Using the CLI module directly

```bash
python -m browser_use.api.server --host 0.0.0.0 --port 8000
```

#### 2. Using uvicorn directly

```bash
uvicorn browser_use.api.server:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Programmatically

```python
from browser_use.api.server import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Environment Variables

Set your LLM API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Example Usage

See the complete example in `examples/api/fastapi_example.py`:

```python
from browser_use.api.fastapi_example import BrowserUseAPIClient

# Direct browser control
client = BrowserUseAPIClient()
await client.create_session(headless=False)
await client.navigate("https://example.com")
state = await client.get_state()
print(f"Page title: {state['title']}")

# Autonomous agent
task_result = await client.run_agent_task(
    "Go to Google and search for 'browser automation'"
)
```

## API Differences from MCP Server

The FastAPI server provides the same functionality as the MCP server but with REST endpoints instead of JSON-RPC:

| MCP Tool | FastAPI Endpoint |
|----------|------------------|
| `browser_navigate` | `POST /browser/navigate` |
| `browser_click` | `POST /browser/click` |
| `browser_type` | `POST /browser/type` |
| `browser_get_state` | `POST /browser/state` |
| `browser_extract_content` | `POST /browser/extract` |
| `retry_with_browser_use_agent` | `POST /agent/task` |

## Session Management

Unlike the MCP server which maintains a single session, the FastAPI server supports multiple concurrent browser sessions. Each session is identified by a `session_id` (defaults to "default").

```python
# Create multiple sessions
await client.create_session("session1", headless=True)
await client.create_session("session2", headless=False)

# Use different sessions
await client.navigate("https://google.com", session_id="session1")
await client.navigate("https://github.com", session_id="session2")
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (session/element not found)
- `500` - Internal Server Error

Example error response:
```json
{
  "detail": "Session session123 not found"
}
```

## Telemetry

The server captures anonymous telemetry data similar to other browser-use components. This can be disabled by setting:

```bash
export ANONYMIZED_TELEMETRY=False
```

## Development

To contribute or modify the FastAPI server:

1. Clone the repository
2. Install development dependencies: `pip install -e ".[all]"`
3. Run the server with auto-reload: `uvicorn browser_use.api.server:app --reload`
4. Access the interactive docs at http://localhost:8000/docs
