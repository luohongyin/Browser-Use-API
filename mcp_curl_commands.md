# Unified MCP Endpoint - Curl Commands
# ====================================
# All browser automation tools accessible through a single endpoint

# Get Available Tools
# ===================

# List all available tools and schema
```bash
curl http://localhost:8000/mcp
```

# Session Management via MCP
# ==========================

# Create a new browser session
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_browser_session",
    "parameters": {
      "session_id": "my_session",
      "headless": true,
      "allowed_domains": [],
      "wait_between_actions": 0.5
    }
  }'
```

# List all active sessions
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_browser_sessions",
    "parameters": {}
  }'
```

# Close a session
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "close_browser_session",
    "parameters": {
      "session_id": "my_session"
    }
  }'
```

# Browser Navigation via MCP
# ===========================

# Navigate to a URL
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_navigate",
    "parameters": {
      "url": "https://example.com",
      "new_tab": false,
      "session_id": "my_session"
    }
  }'
```

# Navigate to URL in new tab
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_navigate",
    "parameters": {
      "url": "https://httpbin.org/html",
      "new_tab": true,
      "session_id": "my_session"
    }
  }'
```

# Get browser state
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_get_state",
    "parameters": {
      "include_screenshot": false,
      "session_id": "my_session"
    }
  }'
```

# Browser Interaction via MCP
# ============================

# Click on element by index
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_click",
    "parameters": {
      "index": 1,
      "new_tab": false,
      "session_id": "my_session"
    }
  }'
```

# Type text into an element
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_type",
    "parameters": {
      "index": 2,
      "text": "Hello World",
      "session_id": "my_session"
    }
  }'
```

# Press keyboard key
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_key",
    "parameters": {
      "key": "Enter",
      "session_id": "my_session"
    }
  }'
```

# Scroll page
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_scroll",
    "parameters": {
      "direction": "down",
      "session_id": "my_session"
    }
  }'
```

# Go back in browser history
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_go_back",
    "parameters": {
      "session_id": "my_session"
    }
  }'
```

# Content Extraction via MCP
# ===========================
# Note: Requires OPENAI_API_KEY environment variable

# Extract content based on query
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_extract_content",
    "parameters": {
      "query": "What is the main heading of this page?",
      "extract_links": false,
      "session_id": "my_session"
    }
  }'
```

# Extract content including links
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_extract_content",
    "parameters": {
      "query": "Extract all the navigation links on this page",
      "extract_links": true,
      "session_id": "my_session"
    }
  }'
```

# Tab Management via MCP
# =======================

# List all open tabs
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_list_tabs",
    "parameters": {
      "session_id": "my_session"
    }
  }'
```

# Switch to tab by index
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_switch_tab",
    "parameters": {
      "tab_index": 1,
      "session_id": "my_session"
    }
  }'
```

# Close tab by index
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_close_tab",
    "parameters": {
      "tab_index": 1,
      "session_id": "my_session"
    }
  }'
```

# Agent Tasks via MCP
# ====================
# Note: Requires OPENAI_API_KEY environment variable

# Run regular agent task
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "run_agent_task",
    "parameters": {
      "task": "Navigate to example.com and find the main heading",
      "max_steps": 10,
      "model": "gpt-4o-mini",
      "session_id": "my_session"
    }
  }'
```

# Retry with browser-use agent
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "retry_with_browser_use_agent",
    "parameters": {
      "task": "Go to httpbin.org and extract information about the IP address endpoint",
      "max_steps": 15,
      "model": "gpt-4o",
      "allowed_domains": ["httpbin.org"],
      "use_vision": true,
      "session_id": "my_session"
    }
  }'
```

# Check agent task status
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_agent_task_status",
    "parameters": {
      "task_id": "task_1234567890"
    }
  }'
```

# Complete Workflow Example via MCP
# ==================================

# 1. Create session
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_browser_session",
    "parameters": {
      "session_id": "demo",
      "headless": true
    }
  }'
```

# 2. Navigate to page
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_navigate",
    "parameters": {
      "url": "https://example.com",
      "session_id": "demo"
    }
  }'
```

# 3. Get page state
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_get_state",
    "parameters": {
      "session_id": "demo"
    }
  }'
```

# 4. Open new tab
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_navigate",
    "parameters": {
      "url": "https://httpbin.org",
      "new_tab": true,
      "session_id": "demo"
    }
  }'
```

# 5. List tabs
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_list_tabs",
    "parameters": {
      "session_id": "demo"
    }
  }'
```

# 6. Switch back to first tab
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_switch_tab",
    "parameters": {
      "tab_index": 0,
      "session_id": "demo"
    }
  }'
```

# 7. Extract content
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser_extract_content",
    "parameters": {
      "query": "What is this website about?",
      "session_id": "demo"
    }
  }'
```

# 8. Close session
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "close_browser_session",
    "parameters": {
      "session_id": "demo"
    }
  }'
```

# Notes:
# ======
# - All tools are accessible through the single /mcp endpoint
# - Use GET /mcp to see available tools and schema
# - Tool names match the original function names
# - Parameters are the same as individual endpoints
# - Session management uses POST instead of DELETE now
# - All LLM-based tools require OPENAI_API_KEY environment variable
