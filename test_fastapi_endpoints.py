#!/usr/bin/env python3
"""
Test script for the enhanced FastAPI server with all MCP server capabilities.
This script demonstrates all the new endpoints added to achieve feature parity.

Run the FastAPI server first:
    uvicorn browser_use.api.standalone_server:app --host 0.0.0.0 --port 8000

Then run this test script:
    python test_fastapi_endpoints.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Helper function to test an endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method.upper()} {endpoint}")
    
    try:
        if method.lower() == 'get':
            response = requests.get(f"{BASE_URL}{endpoint}")
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    print("Testing Enhanced FastAPI Server - All MCP Server Capabilities")
    print("=" * 60)
    
    # Test server health
    test_endpoint("GET", "/", description="Server root endpoint")
    test_endpoint("GET", "/health", description="Health check")
    
    # Create a session
    test_endpoint("POST", "/sessions", {
        "session_id": "test_session",
        "headless": True,
        "allowed_domains": [],
        "wait_between_actions": 0.5
    }, description="Create browser session")
    
    # Navigate to a website
    test_endpoint("POST", "/browser/navigate", {
        "url": "https://example.com",
        "new_tab": False,
        "session_id": "test_session"
    }, description="Navigate to example.com")
    
    # Get browser state
    test_endpoint("POST", "/browser/state", {
        "include_screenshot": False,
        "session_id": "test_session"
    }, description="Get browser state")
    
    # Test scrolling
    test_endpoint("POST", "/browser/scroll", {
        "direction": "down",
        "session_id": "test_session"
    }, description="Scroll down")
    
    # Test keyboard input
    test_endpoint("POST", "/browser/key", {
        "key": "F5",
        "session_id": "test_session"
    }, description="Press F5 key (refresh)")
    
    # Test content extraction (requires OPENAI_API_KEY)
    test_endpoint("POST", "/browser/extract_content", {
        "query": "What is the main heading of this page?",
        "extract_links": False,
        "session_id": "test_session"
    }, description="Extract content with LLM")
    
    # Test tab management - open new tab
    test_endpoint("POST", "/browser/navigate", {
        "url": "https://httpbin.org/html",
        "new_tab": True,
        "session_id": "test_session"
    }, description="Open new tab")
    
    # List tabs
    test_endpoint("POST", "/browser/list_tabs", {
        "session_id": "test_session"
    }, description="List all tabs")
    
    # Switch to first tab
    test_endpoint("POST", "/browser/switch_tab", {
        "tab_index": 0,
        "session_id": "test_session"
    }, description="Switch to first tab")
    
    # Go back in history
    test_endpoint("POST", "/browser/go_back", {
        "session_id": "test_session"
    }, description="Go back in browser history")
    
    # Close second tab if it exists
    test_endpoint("POST", "/browser/close_tab", {
        "tab_index": 1,
        "session_id": "test_session"
    }, description="Close second tab")
    
    # Test retry with agent (requires OPENAI_API_KEY)
    test_endpoint("POST", "/browser/retry_with_agent", {
        "task": "Navigate to https://example.com and tell me what the main heading says",
        "max_steps": 5,
        "model": "gpt-4o-mini",
        "allowed_domains": ["example.com"],
        "use_vision": True,
        "session_id": "test_session"
    }, description="Retry task with autonomous agent")
    
    # List sessions
    test_endpoint("GET", "/sessions", description="List all sessions")
    
    print(f"\n{'='*60}")
    print("Test completed! Check the server logs for detailed output.")
    print("Note: Some endpoints require OPENAI_API_KEY environment variable.")

if __name__ == "__main__":
    main()
