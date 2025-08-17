# Enhanced FastAPI Server - All Endpoints Curl Commands
# ==================================================
# Complete curl command reference for all MCP server capabilities now available in FastAPI

# Server Status and Health
# ========================

# Check server status
```bash
curl http://localhost:8000/
```

# Health check
```bash
curl http://localhost:8000/health
```

# Session Management
# ==================

# Create a new browser session
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "headless": false,
    "allowed_domains": [],
    "wait_between_actions": 0.5
  }'
```

# List all active sessions
```bash
curl http://localhost:8000/sessions
```

# Close a session
```bash
curl -X DELETE http://localhost:8000/sessions/my_session
```

# Basic Browser Control
# =====================

# Navigate to a URL
```bash
curl -X POST http://localhost:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://google.com",
    "new_tab": false,
    "session_id": "my_session"
  }'
```

# Navigate to URL in new tab
```bash
curl -X POST http://localhost:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html",
    "new_tab": true,
    "session_id": "my_session"
  }'
```

# Get browser state (shows all interactive elements)
```bash
curl -X POST http://localhost:8000/browser/state \
  -H "Content-Type: application/json" \
  -d '{
    "include_screenshot": false,
    "session_id": "my_session"
  }'
```

# Click on element by index
```bash
curl -X POST http://localhost:8000/browser/click \
  -H "Content-Type: application/json" \
  -d '{
    "index": 1,
    "new_tab": false,
    "session_id": "my_session"
  }'
```

# Type text into an input field
```bash
curl -X POST http://localhost:8000/browser/type \
  -H "Content-Type: application/json" \
  -d '{
    "index": 2,
    "text": "Hello World",
    "session_id": "my_session"
  }'
```

# Keyboard Input (NEW)
# ===================

# Press Enter key
```bash
curl -X POST http://localhost:8000/browser/key \
  -H "Content-Type: application/json" \
  -d '{
    "key": "Enter",
    "session_id": "my_session"
  }'
```

# Press Tab key
```bash
curl -X POST http://localhost:8000/browser/key \
  -H "Content-Type: application/json" \
  -d '{
    "key": "Tab",
    "session_id": "my_session"
  }'
```

# Press Escape key
```bash
curl -X POST http://localhost:8000/browser/key \
  -H "Content-Type: application/json" \
  -d '{
    "key": "Escape",
    "session_id": "my_session"
  }'
```

# Page Interaction
# ================

# Scroll down
```bash
curl -X POST http://localhost:8000/browser/scroll \
  -H "Content-Type: application/json" \
  -d '{
    "direction": "down",
    "session_id": "my_session"
  }'
```

# Scroll up
```bash
curl -X POST http://localhost:8000/browser/scroll \
  -H "Content-Type: application/json" \
  -d '{
    "direction": "up",
    "session_id": "my_session"
  }'
```

# Go back in browser history (NEW)
```bash
curl -X POST http://localhost:8000/browser/go_back \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session"
  }'
```

# Content Extraction with LLM (NEW)
# ==================================
# Note: Requires OPENAI_API_KEY environment variable

# Extract content based on query
```bash
curl -X POST http://localhost:8000/browser/extract_content \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main heading of this page?",
    "extract_links": false,
    "session_id": "my_session"
  }'
```

# Extract content including links
```bash
curl -X POST http://localhost:8000/browser/extract_content \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Extract all the navigation links on this page",
    "extract_links": true,
    "session_id": "my_session"
  }'
```

# Tab Management (NEW)
# ====================

# List all open tabs
```bash
curl -X POST http://localhost:8000/browser/list_tabs \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session"
  }'
```

# Switch to tab by index
```bash
curl -X POST http://localhost:8000/browser/switch_tab \
  -H "Content-Type: application/json" \
  -d '{
    "tab_index": 1,
    "session_id": "my_session"
  }'
```

# Close tab by index
```bash
curl -X POST http://localhost:8000/browser/close_tab \
  -H "Content-Type: application/json" \
  -d '{
    "tab_index": 1,
    "session_id": "my_session"
  }'
```

# Autonomous Agent Tasks
# ======================

# Run regular agent task
```bash
curl -X POST http://localhost:8000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Navigate to example.com and find the main heading",
    "max_steps": 10,
    "model": "gpt-4o-mini",
    "session_id": "my_session"
  }'
```

# Retry with browser-use agent (NEW - Fallback option)
# Note: Creates independent session, requires OPENAI_API_KEY
```bash
curl -X POST http://localhost:8000/browser/retry_with_agent \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to httpbin.org and extract information about the IP address endpoint",
    "max_steps": 15,
    "model": "gpt-4o",
    "allowed_domains": ["httpbin.org"],
    "use_vision": true,
    "session_id": "my_session"
  }'
```

# Check agent task status
```bash
curl http://localhost:8000/agent/task/task_1234567890
```

# Example Workflow: Complete Tab Management
# =========================================

# 1. Create session
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "headless": true}'
```

# 2. Open first page
```bash
curl -X POST http://localhost:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "session_id": "demo"}'
```

# 3. Open second page in new tab
```bash
curl -X POST http://localhost:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org", "new_tab": true, "session_id": "demo"}'
```

# 4. List tabs
```bash
curl -X POST http://localhost:8000/browser/list_tabs \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo"}'
```

# 5. Switch back to first tab
```bash
curl -X POST http://localhost:8000/browser/switch_tab \
  -H "Content-Type: application/json" \
  -d '{"tab_index": 0, "session_id": "demo"}'
```

# 6. Extract content from current page
```bash
curl -X POST http://localhost:8000/browser/extract_content \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this website about?", "session_id": "my_session"}'
```

# 7. Close the second tab
```bash
curl -X POST http://localhost:8000/browser/close_tab \
  -H "Content-Type: application/json" \
  -d '{"tab_index": 1, "session_id": "demo"}'
```

# 8. Clean up - close session
```bash
curl -X DELETE http://localhost:8000/sessions/demo
```

# Advanced Features Demonstration
# ===============================

# Form filling example with keyboard support
# 1. Navigate to a form page
```bash
curl -X POST http://localhost:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/forms/post", "session_id": "demo"}'
```

# 2. Get page state to find form elements
```bash
curl -X POST http://localhost:8000/browser/state \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo"}'
```

# 3. Click on first input field (assuming index 1)
```bash
curl -X POST http://localhost:8000/browser/click \
  -H "Content-Type: application/json" \
  -d '{"index": 1, "session_id": "demo"}'
```

# 4. Type in the field
```bash
curl -X POST http://localhost:8000/browser/type \
  -H "Content-Type: application/json" \
  -d '{"index": 1, "text": "test@example.com", "session_id": "demo"}'
```

# 5. Press Tab to move to next field
```bash
curl -X POST http://localhost:8000/browser/key \
  -H "Content-Type: application/json" \
  -d '{"key": "Tab", "session_id": "demo"}'
```

# 6. Type in next field (assuming index 2)
```bash
curl -X POST http://localhost:8000/browser/type \
  -H "Content-Type: application/json" \
  -d '{"index": 2, "text": "password123", "session_id": "demo"}'
```

# 7. Press Enter to submit form
```bash
curl -X POST http://localhost:8000/browser/key \
  -H "Content-Type: application/json" \
  -d '{"key": "Enter", "session_id": "demo"}'
```

# Notes:
# ======
# - All endpoints that require LLM functionality need OPENAI_API_KEY environment variable
# - Session IDs are required for all browser operations
# - Tab indices start from 0
# - The retry_with_agent endpoint creates its own independent browser session
# - Use "gpt-4o-mini" for cost-effective operations, "gpt-4o" for complex tasks
# - Always check the element indices with browser/state before clicking or typing
