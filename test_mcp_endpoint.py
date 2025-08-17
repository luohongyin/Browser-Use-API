#!/usr/bin/env python3
"""
Test script for the unified MCP endpoint in the FastAPI server.

Run the FastAPI server first:
    uvicorn browser_use.api.standalone_server:app --host 0.0.0.0 --port 8000

Then run this test script:
    python test_mcp_endpoint.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_mcp_endpoint(tool_name, parameters, description=""):
    """Helper function to test the MCP endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Tool: {tool_name}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/mcp", json={
            "tool_name": tool_name,
            "parameters": parameters
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    print("Testing Unified MCP Endpoint")
    print("=" * 60)
    
    # Test GET endpoint for available tools
    print("\n1. Getting available tools...")
    try:
        response = requests.get(f"{BASE_URL}/mcp")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Available tools: {len(result['available_tools'])}")
            print(f"Tools: {', '.join(result['available_tools'])}")
    except Exception as e:
        print(f"Failed to get tools: {e}")
    
    # Test session management via MCP endpoint
    test_mcp_endpoint(
        "create_browser_session",
        {
            "session_id": "mcp_test_session",
            "headless": True,
            "allowed_domains": [],
            "wait_between_actions": 0.5
        },
        "Create browser session via MCP"
    )
    
    # Test navigation via MCP endpoint
    test_mcp_endpoint(
        "browser_navigate",
        {
            "url": "https://example.com",
            "new_tab": False,
            "session_id": "mcp_test_session"
        },
        "Navigate to example.com via MCP"
    )
    
    # Test getting browser state via MCP endpoint
    test_mcp_endpoint(
        "browser_get_state",
        {
            "include_screenshot": False,
            "session_id": "mcp_test_session"
        },
        "Get browser state via MCP"
    )
    
    # Test scrolling via MCP endpoint
    test_mcp_endpoint(
        "browser_scroll",
        {
            "direction": "down",
            "session_id": "mcp_test_session"
        },
        "Scroll page down via MCP"
    )
    
    # Test keyboard input via MCP endpoint
    test_mcp_endpoint(
        "browser_key",
        {
            "key": "F5",
            "session_id": "mcp_test_session"
        },
        "Press F5 key via MCP"
    )
    
    # Test tab management via MCP endpoint
    test_mcp_endpoint(
        "browser_navigate",
        {
            "url": "https://httpbin.org/html",
            "new_tab": True,
            "session_id": "mcp_test_session"
        },
        "Open new tab via MCP"
    )
    
    test_mcp_endpoint(
        "browser_list_tabs",
        {
            "session_id": "mcp_test_session"
        },
        "List tabs via MCP"
    )
    
    test_mcp_endpoint(
        "browser_switch_tab",
        {
            "tab_index": 0,
            "session_id": "mcp_test_session"
        },
        "Switch to first tab via MCP"
    )
    
    # Test content extraction via MCP endpoint (requires OPENAI_API_KEY)
    test_mcp_endpoint(
        "browser_extract_content",
        {
            "query": "What is the main heading of this page?",
            "extract_links": False,
            "session_id": "mcp_test_session"
        },
        "Extract content via MCP (requires OPENAI_API_KEY)"
    )
    
    # Test session listing via MCP endpoint
    test_mcp_endpoint(
        "list_browser_sessions",
        {},
        "List all sessions via MCP"
    )
    
    # Test agent task via MCP endpoint (requires OPENAI_API_KEY)
    test_mcp_endpoint(
        "retry_with_browser_use_agent",
        {
            "task": "Navigate to example.com and tell me what the main heading says",
            "max_steps": 5,
            "model": "gpt-4o-mini",
            "allowed_domains": ["example.com"],
            "use_vision": True,
            "session_id": "mcp_test_session"
        },
        "Run agent task via MCP (requires OPENAI_API_KEY)"
    )
    
    # Test session closure via MCP endpoint
    test_mcp_endpoint(
        "close_browser_session",
        {
            "session_id": "mcp_test_session"
        },
        "Close session via MCP"
    )
    
    # Test invalid tool
    test_mcp_endpoint(
        "invalid_tool",
        {},
        "Test invalid tool (should fail)"
    )
    
    print(f"\n{'='*60}")
    print("MCP endpoint testing completed!")
    print("The unified endpoint provides a single interface for all browser automation tools.")

if __name__ == "__main__":
    main()
