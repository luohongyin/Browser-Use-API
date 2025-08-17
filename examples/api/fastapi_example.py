"""Example usage of the browser-use FastAPI server"""

import asyncio
import json
import httpx
from typing import Dict, Any

class BrowserUseAPIClient:
    """Simple client for the browser-use API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = "default"
    
    async def create_session(self, headless: bool = True, allowed_domains: list | None = None) -> Dict[str, Any]:
        """Create a browser session"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sessions",
                json={
                    "session_id": self.session_id,
                    "headless": headless,
                    "allowed_domains": allowed_domains or [],
                    "wait_between_actions": 0.5
                }
            )
            return response.json()
    
    async def navigate(self, url: str, new_tab: bool = False) -> Dict[str, Any]:
        """Navigate to a URL"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/browser/navigate",
                json={
                    "url": url,
                    "new_tab": new_tab,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def get_state(self, include_screenshot: bool = False) -> Dict[str, Any]:
        """Get current browser state"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/browser/state",
                json={
                    "include_screenshot": include_screenshot,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def click(self, index: int, new_tab: bool = False) -> Dict[str, Any]:
        """Click an element by index"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/browser/click",
                json={
                    "index": index,
                    "new_tab": new_tab,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def type_text(self, index: int, text: str) -> Dict[str, Any]:
        """Type text into an element"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/browser/type",
                json={
                    "index": index,
                    "text": text,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def extract_content(self, query: str, extract_links: bool = False) -> Dict[str, Any]:
        """Extract content from the current page"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/browser/extract",
                json={
                    "query": query,
                    "extract_links": extract_links,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def run_agent_task(self, task: str, max_steps: int = 100, model: str = "gpt-4o") -> Dict[str, Any]:
        """Run an autonomous agent task"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/agent/task",
                json={
                    "task": task,
                    "max_steps": max_steps,
                    "model": model,
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of an agent task"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/agent/task/{task_id}")
            return response.json()
    
    async def close_session(self) -> Dict[str, Any]:
        """Close the browser session"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/sessions/{self.session_id}")
            return response.json()

async def example_direct_browser_control():
    """Example of direct browser control"""
    client = BrowserUseAPIClient()
    
    print("Creating browser session...")
    result = await client.create_session(headless=False)
    print(f"Session created: {result}")
    
    print("Navigating to Google...")
    result = await client.navigate("https://www.google.com")
    print(f"Navigation: {result}")
    
    print("Getting page state...")
    state = await client.get_state()
    print(f"Page title: {state['title']}")
    print(f"Found {len(state['interactive_elements'])} interactive elements")
    
    # Find search input
    search_input = None
    for element in state['interactive_elements']:
        if element['tag'] == 'input' and 'search' in element.get('placeholder', '').lower():
            search_input = element['index']
            break
    
    if search_input is not None:
        print(f"Typing in search box (index {search_input})...")
        await client.type_text(search_input, "browser automation")
        
        # Find search button
        for element in state['interactive_elements']:
            if element['tag'] == 'input' and element.get('text', '').strip() in ['Google Search', 'Search']:
                print(f"Clicking search button (index {element['index']})...")
                await client.click(element['index'])
                break
    
    print("Extracting search results...")
    content = await client.extract_content("Extract the first 3 search result titles")
    print(f"Extracted content: {content}")
    
    print("Closing session...")
    await client.close_session()

async def example_agent_task():
    """Example of using the autonomous agent"""
    client = BrowserUseAPIClient()
    
    print("Creating browser session...")
    await client.create_session(headless=False)
    
    print("Starting agent task...")
    task_result = await client.run_agent_task(
        "Go to Google, search for 'FastAPI documentation', and extract the main features mentioned on the official FastAPI documentation page"
    )
    print(f"Task started: {task_result}")
    
    # Poll for completion
    task_id = task_result['task_id']
    print(f"Monitoring task {task_id}...")
    
    while True:
        status = await client.get_task_status(task_id)
        print(f"Status: {status['status']}")
        
        if status['status'] == 'completed':
            if 'final_result' in status:
                print(f"Final result: {status['final_result']}")
            if 'urls_visited' in status:
                print(f"URLs visited: {status['urls_visited']}")
            break
        
        await asyncio.sleep(2)
    
    print("Closing session...")
    await client.close_session()

if __name__ == "__main__":
    print("Browser-Use FastAPI Example")
    print("1. Direct browser control example")
    print("2. Autonomous agent example")
    
    choice = input("Choose example (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(example_direct_browser_control())
    elif choice == "2":
        asyncio.run(example_agent_task())
    else:
        print("Invalid choice")
