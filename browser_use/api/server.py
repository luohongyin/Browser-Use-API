"""FastAPI Server for browser-use - exposes browser automation capabilities via REST API.

This server provides endpoints for:
- Running autonomous browser tasks with an AI agent
- Direct browser control (navigation, clicking, typing, etc.)
- Content extraction from web pages
- File system operations

Usage:
    uvicorn browser_use.api.server:app --host 0.0.0.0 --port 8000

Or programmatically:
    from browser_use.api.server import create_app
    app = create_app()
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing_extensions import Annotated
import uvicorn

# Add browser-use to path if running from source
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import and configure logging
from browser_use.logging_config import setup_logging

# Set up logging for API server
os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'info'
setup_logging(stream=sys.stderr, log_level='info')

# Import browser_use modules
from browser_use import ActionModel, Agent
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.config import get_default_llm, get_default_profile, load_browser_use_config
from browser_use.controller.service import Controller
from browser_use.filesystem.file_system import FileSystem
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.telemetry import CLITelemetryEvent, ProductTelemetry
from browser_use.telemetry.views import BaseTelemetryEvent
from browser_use.utils import get_browser_use_version
from dataclasses import dataclass

@dataclass
class APIServerTelemetryEvent(BaseTelemetryEvent):
    """Telemetry event for API server usage"""
    
    version: str
    action: str  # 'start', 'stop', 'tool_call'
    tool_name: str | None = None
    duration_seconds: float | None = None
    error_message: str | None = None
    
    name: str = 'api_server_event'

logger = logging.getLogger(__name__)

# Global state management
class ServerState:
    def __init__(self):
        self.browser_sessions: Dict[str, BrowserSession] = {}
        self.agents: Dict[str, Agent] = {}
        self.controllers: Dict[str, Controller] = {}
        self.file_systems: Dict[str, FileSystem] = {}
        self.config = load_browser_use_config()
        self.telemetry = ProductTelemetry()
        self.start_time = time.time()

    async def cleanup(self):
        """Clean up all active sessions"""
        logger.info("Cleaning up server state...")
        
        # Close all agents
        for agent_id, agent in self.agents.items():
            try:
                await agent.close()
                logger.debug(f"Closed agent {agent_id}")
            except Exception as e:
                logger.error(f"Error closing agent {agent_id}: {e}")
        
        # Close all browser sessions
        for session_id, session in self.browser_sessions.items():
            try:
                await session.stop()
                logger.debug(f"Closed browser session {session_id}")
            except Exception as e:
                logger.error(f"Error closing browser session {session_id}: {e}")
        
        # Capture telemetry for server stop
        duration = time.time() - self.start_time
        self.telemetry.capture(
            APIServerTelemetryEvent(
                version=get_browser_use_version(),
                action='stop',
                duration_seconds=duration,
            )
        )
        self.telemetry.flush()

# Global server state
server_state = ServerState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle server startup and shutdown"""
    # Startup
    logger.info("Starting browser-use API server")
    server_state.telemetry.capture(
        APIServerTelemetryEvent(
            version=get_browser_use_version(),
            action='start',
        )
    )
    
    yield
    
    # Shutdown
    await server_state.cleanup()

# Pydantic models for API requests and responses

class BrowserNavigateRequest(BaseModel):
    url: str = Field(..., description="The URL to navigate to")
    new_tab: bool = Field(False, description="Whether to open in a new tab")
    session_id: str = Field("default", description="Browser session ID")

class BrowserClickRequest(BaseModel):
    index: int = Field(..., description="The index of the element to click")
    new_tab: bool = Field(False, description="Whether to open in a new tab")
    session_id: str = Field("default", description="Browser session ID")

class BrowserTypeRequest(BaseModel):
    index: int = Field(..., description="The index of the input element")
    text: str = Field(..., description="The text to type")
    session_id: str = Field("default", description="Browser session ID")

class BrowserStateRequest(BaseModel):
    include_screenshot: bool = Field(False, description="Whether to include a screenshot")
    session_id: str = Field("default", description="Browser session ID")

class BrowserExtractRequest(BaseModel):
    query: str = Field(..., description="What information to extract from the page")
    extract_links: bool = Field(False, description="Whether to include links in the extraction")
    session_id: str = Field("default", description="Browser session ID")

class BrowserScrollRequest(BaseModel):
    direction: Annotated[str, Field(description="Direction to scroll")] = "down"
    session_id: str = "default"
    
    class Config:
        schema_extra = {
            "properties": {
                "direction": {"enum": ["up", "down"]}
            }
        }

class BrowserTabRequest(BaseModel):
    session_id: str = Field("default", description="Browser session ID")

class BrowserSwitchTabRequest(BaseModel):
    tab_index: int = Field(..., description="Index of the tab to switch to")
    session_id: str = Field("default", description="Browser session ID")

class BrowserCloseTabRequest(BaseModel):
    tab_index: int = Field(..., description="Index of the tab to close")
    session_id: str = Field("default", description="Browser session ID")

class AgentTaskRequest(BaseModel):
    task: str = Field(..., description="The task description for the agent")
    max_steps: int = Field(100, description="Maximum number of steps the agent can take")
    model: str = Field("gpt-4o", description="LLM model to use")
    allowed_domains: List[str] = Field([], description="List of allowed domains")
    use_vision: bool = Field(True, description="Whether to use vision capabilities")
    session_id: str = Field("default", description="Browser session ID")

class CreateSessionRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Custom session ID (auto-generated if not provided)")
    headless: bool = Field(True, description="Whether to run browser in headless mode")
    allowed_domains: List[str] = Field([], description="List of allowed domains")
    wait_between_actions: float = Field(0.5, description="Wait time between actions")
    user_data_dir: Optional[str] = Field(None, description="Custom user data directory")

class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    session_id: str

class BrowserStateResponse(BaseModel):
    url: str
    title: str
    tabs: List[Dict[str, str]]
    interactive_elements: List[Dict[str, Any]]
    screenshot: Optional[str] = None

# Create FastAPI app
def create_app() -> FastAPI:
    app = FastAPI(
        title="Browser-Use API",
        description="REST API for browser automation capabilities",
        version=get_browser_use_version(),
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "Browser-Use API Server",
            "version": get_browser_use_version(),
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "active_sessions": len(server_state.browser_sessions),
            "active_agents": len(server_state.agents)
        }

    # Session management endpoints
    @app.post("/sessions", response_model=SessionResponse)
    async def create_session(request: CreateSessionRequest):
        """Create a new browser session"""
        try:
            session_id = request.session_id or f"session_{int(time.time() * 1000)}"
            
            if session_id in server_state.browser_sessions:
                raise HTTPException(status_code=400, detail=f"Session {session_id} already exists")

            # Get profile config and merge with request parameters
            profile_config = get_default_profile(server_state.config)
            
            profile_data = {
                'downloads_path': str(Path.home() / 'Downloads' / 'browser-use-api'),
                'wait_between_actions': request.wait_between_actions,
                'keep_alive': True,
                'user_data_dir': request.user_data_dir or '~/.config/browseruse/profiles/api',
                'headless': request.headless,
                'allowed_domains': request.allowed_domains,
                **profile_config,
            }

            # Create browser profile and session
            profile = BrowserProfile(**profile_data)
            session = BrowserSession(browser_profile=profile)
            await session.start()

            # Store session and create controller
            server_state.browser_sessions[session_id] = session
            server_state.controllers[session_id] = Controller()

            # Initialize FileSystem
            file_system_path = profile_config.get('file_system_path', '~/.browser-use-api')
            server_state.file_systems[session_id] = FileSystem(base_dir=Path(file_system_path).expanduser())

            logger.info(f"Created browser session {session_id}")
            
            return SessionResponse(
                session_id=session_id,
                status="created",
                message=f"Browser session {session_id} created successfully"
            )

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/sessions/{session_id}")
    async def close_session(session_id: str):
        """Close a browser session"""
        try:
            if session_id not in server_state.browser_sessions:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

            # Close agent if exists
            if session_id in server_state.agents:
                await server_state.agents[session_id].close()
                del server_state.agents[session_id]

            # Close browser session
            session = server_state.browser_sessions[session_id]
            await session.stop()
            del server_state.browser_sessions[session_id]

            # Clean up other resources
            if session_id in server_state.controllers:
                del server_state.controllers[session_id]
            if session_id in server_state.file_systems:
                del server_state.file_systems[session_id]

            logger.info(f"Closed browser session {session_id}")
            
            return {"message": f"Session {session_id} closed successfully"}

        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/sessions")
    async def list_sessions():
        """List all active browser sessions"""
        sessions = []
        for session_id, session in server_state.browser_sessions.items():
            try:
                current_page = await session.get_current_page()
                sessions.append({
                    "session_id": session_id,
                    "url": current_page.url if current_page else None,
                    "title": await current_page.title() if current_page and not current_page.is_closed() else None,
                    "has_agent": session_id in server_state.agents
                })
            except Exception as e:
                sessions.append({
                    "session_id": session_id,
                    "error": str(e),
                    "has_agent": session_id in server_state.agents
                })
        
        return {"sessions": sessions}

    # Helper function to get or create session
    async def get_session(session_id: str) -> BrowserSession:
        # Auto-create default session
        if session_id not in server_state.browser_sessions:
            if session_id == "default":
                # Create default session with sensible defaults
                default_request = CreateSessionRequest(
                    session_id="default",
                    headless=True,
                    allowed_domains=[],
                    wait_between_actions=0.5,
                    user_data_dir=None
                )
                await create_session(default_request)
            else:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return server_state.browser_sessions[session_id]

    # Browser control endpoints
    @app.post("/browser/navigate")
    async def browser_navigate(request: BrowserNavigateRequest):
        """Navigate to a URL"""
        try:
            session = await get_session(request.session_id)
            
            if request.new_tab:
                page = await session.create_new_tab(request.url)
                tab_idx = session.tabs.index(page)
                message = f'Opened new tab #{tab_idx} with URL: {request.url}'
            else:
                await session.navigate_to(request.url)
                message = f'Navigated to: {request.url}'

            return {"message": message}

        except Exception as e:
            logger.error(f"Error navigating: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/click")
    async def browser_click(request: BrowserClickRequest):
        """Click an element by index"""
        try:
            session = await get_session(request.session_id)
            
            element = await session.get_dom_element_by_index(request.index)
            if not element:
                raise HTTPException(status_code=404, detail=f'Element with index {request.index} not found')

            if request.new_tab:
                # Handle new tab logic (similar to MCP server)
                href = element.attributes.get('href')
                if href:
                    from urllib.parse import urlparse
                    current_page = await session.get_current_page()
                    if href.startswith('/'):
                        parsed = urlparse(current_page.url)
                        full_url = f'{parsed.scheme}://{parsed.netloc}{href}'
                    else:
                        full_url = href

                    page = await session.create_new_tab(full_url)
                    tab_idx = session.tabs.index(page)
                    message = f'Clicked element {request.index} and opened in new tab #{tab_idx}'
                else:
                    # Ctrl/Cmd+Click for non-links
                    element_handle = await session.get_locate_element(element)
                    if element_handle:
                        modifier = 'Meta' if sys.platform == 'darwin' else 'Control'
                        await element_handle.click(modifiers=[modifier])
                        await asyncio.sleep(0.5)
                        message = f'Clicked element {request.index} with {modifier} key (new tab if supported)'
                    else:
                        raise HTTPException(status_code=500, detail=f'Could not locate element {request.index} for modified click')
            else:
                await session._click_element_node(element)
                message = f'Clicked element {request.index}'

            return {"message": message}

        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/type")
    async def browser_type(request: BrowserTypeRequest):
        """Type text into an element"""
        try:
            session = await get_session(request.session_id)
            
            element = await session.get_dom_element_by_index(request.index)
            if not element:
                raise HTTPException(status_code=404, detail=f'Element with index {request.index} not found')

            await session._input_text_element_node(element, request.text)
            return {"message": f"Typed '{request.text}' into element {request.index}"}

        except Exception as e:
            logger.error(f"Error typing text: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/state", response_model=BrowserStateResponse)
    async def get_browser_state(request: BrowserStateRequest):
        """Get current browser state"""
        try:
            session = await get_session(request.session_id)
            
            state = await session.get_browser_state_with_recovery(cache_clickable_elements_hashes=False)

            interactive_elements = []
            for index, element in state.selector_map.items():
                elem_info = {
                    'index': index,
                    'tag': element.tag_name,
                    'text': element.get_all_text_till_next_clickable_element(max_depth=2)[:100],
                }
                if element.attributes.get('placeholder'):
                    elem_info['placeholder'] = element.attributes['placeholder']
                if element.attributes.get('href'):
                    elem_info['href'] = element.attributes['href']
                interactive_elements.append(elem_info)

            response_data = {
                'url': state.url,
                'title': state.title,
                'tabs': [{'url': tab.url, 'title': tab.title} for tab in state.tabs],
                'interactive_elements': interactive_elements,
            }

            if request.include_screenshot and state.screenshot:
                response_data['screenshot'] = state.screenshot

            return BrowserStateResponse(**response_data)

        except Exception as e:
            logger.error(f"Error getting browser state: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/extract")
    async def browser_extract_content(request: BrowserExtractRequest):
        """Extract content from current page"""
        try:
            session = await get_session(request.session_id)
            
            # Need LLM for extraction
            llm_config = get_default_llm(server_state.config)
            api_key = llm_config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=400, detail='OPENAI_API_KEY not set in config or environment')

            llm = ChatOpenAI(
                model=llm_config.get('model', 'gpt-4o'),
                api_key=api_key,
                temperature=llm_config.get('temperature', 0.7),
            )

            controller = server_state.controllers[request.session_id]
            file_system = server_state.file_systems[request.session_id]

            # Create dynamic action model for extraction
            from pydantic import create_model
            ExtractAction = create_model(
                'ExtractAction',
                __base__=ActionModel,
                extract_structured_data=(dict[str, Any], {'query': request.query, 'extract_links': request.extract_links}),
            )

            action = ExtractAction()
            action_result = await controller.act(
                action=action,
                browser_session=session,
                page_extraction_llm=llm,
                file_system=file_system,
            )

            content = action_result.extracted_content or 'No content extracted'
            return {"content": content}

        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/scroll")
    async def browser_scroll(request: BrowserScrollRequest):
        """Scroll the page"""
        try:
            session = await get_session(request.session_id)
            
            page = await session.get_current_page()
            viewport_height = await page.evaluate('() => window.innerHeight')
            dy = viewport_height if request.direction == 'down' else -viewport_height

            await page.evaluate('(y) => window.scrollBy(0, y)', dy)
            return {"message": f'Scrolled {request.direction}'}

        except Exception as e:
            logger.error(f"Error scrolling: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/back")
    async def browser_go_back(request: BrowserTabRequest):
        """Go back in browser history"""
        try:
            session = await get_session(request.session_id)
            await session.go_back()
            return {"message": 'Navigated back'}

        except Exception as e:
            logger.error(f"Error going back: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/browser/tabs")
    async def browser_list_tabs(session_id: str = "default"):
        """List all open tabs"""
        try:
            session = await get_session(session_id)
            
            tabs = []
            for i, tab in enumerate(session.tabs):
                tabs.append({
                    'index': i, 
                    'url': tab.url, 
                    'title': await tab.title() if not tab.is_closed() else 'Closed'
                })
            return {"tabs": tabs}

        except Exception as e:
            logger.error(f"Error listing tabs: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/tabs/switch")
    async def browser_switch_tab(request: BrowserSwitchTabRequest):
        """Switch to a different tab"""
        try:
            session = await get_session(request.session_id)
            
            await session.switch_to_tab(request.tab_index)
            page = await session.get_current_page()
            return {"message": f'Switched to tab {request.tab_index}: {page.url}'}

        except Exception as e:
            logger.error(f"Error switching tab: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/browser/tabs/close")
    async def browser_close_tab(request: BrowserCloseTabRequest):
        """Close a specific tab"""
        try:
            session = await get_session(request.session_id)
            
            if 0 <= request.tab_index < len(session.tabs):
                tab = session.tabs[request.tab_index]
                url = tab.url
                await tab.close()
                return {"message": f'Closed tab {request.tab_index}: {url}'}
            else:
                raise HTTPException(status_code=400, detail=f'Invalid tab index: {request.tab_index}')

        except Exception as e:
            logger.error(f"Error closing tab: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Agent endpoints
    @app.post("/agent/task", response_model=TaskResponse)
    async def run_agent_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
        """Run an autonomous agent task"""
        try:
            session = await get_session(request.session_id)
            
            # Get LLM config
            llm_config = get_default_llm(server_state.config)
            api_key = llm_config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=400, detail='OPENAI_API_KEY not set in config or environment')

            llm = ChatOpenAI(
                model=request.model,
                api_key=api_key,
                temperature=llm_config.get('temperature', 0.7),
            )

            # Create agent
            agent = Agent(
                task=request.task,
                llm=llm,
                browser_session=session,
                use_vision=request.use_vision,
            )

            # Store agent
            task_id = f"task_{int(time.time() * 1000)}"
            server_state.agents[task_id] = agent

            # Run agent in background
            async def run_agent():
                try:
                    await agent.run(max_steps=request.max_steps)
                    logger.info(f"Agent task {task_id} completed successfully")
                except Exception as e:
                    logger.error(f"Agent task {task_id} failed: {e}")

            background_tasks.add_task(run_agent)

            return TaskResponse(
                task_id=task_id,
                status="started",
                message=f"Agent task {task_id} started",
                session_id=request.session_id
            )

        except Exception as e:
            logger.error(f"Error running agent task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent/task/{task_id}")
    async def get_agent_task_status(task_id: str):
        """Get the status of an agent task"""
        if task_id not in server_state.agents:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        agent = server_state.agents[task_id]
        
        # Check if agent is still running
        is_running = hasattr(agent, 'running') and getattr(agent, 'running', False)
        
        # Get history if available
        history_info = {}
        if hasattr(agent, 'state') and hasattr(agent.state, 'history'):
            history = agent.state.history
            history_info = {
                "steps_completed": len(history.history),
                "is_successful": history.is_successful(),
                "total_duration": history.total_duration_seconds(),
                "urls_visited": [str(url) for url in history.urls() if url is not None],
            }
            
            # Get final result if available
            final_result = history.final_result()
            if final_result:
                history_info["final_result"] = final_result
            
            # Get errors if any
            errors = history.errors()
            if errors:
                history_info["errors"] = errors

        return {
            "task_id": task_id,
            "status": "running" if is_running else "completed",
            **history_info
        }

    return app

# Create app instance
app = create_app()

def main():
    """Main entry point for running the server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser-Use FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "browser_use.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
