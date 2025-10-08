#!/usr/bin/env python3
"""
Historical Facts MCP HTTP Server

Enhanced HTTP server that provides both REST API endpoints AND a proper /mcp 
endpoint for ChatGPT Desktop integration. This server supports:

1. REST API endpoints (for web frontend)
2. /mcp endpoint for ChatGPT Desktop connection
3. Proper MCP protocol over HTTP

Author: suspicious_kowalevski
License: MIT
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Union
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

# Import our existing MCP server functionality
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Wikipedia On This Day API base URL
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historical-facts-mcp-http")


async def fetch_historical_events(month: int, day: int, event_type: str = "all") -> dict:
    """Fetch historical events from Wikipedia's On This Day API"""
    try:
        if event_type == "all":
            url = f"{WIKI_API_BASE}/all/{month:02d}/{day:02d}"
        else:
            url = f"{WIKI_API_BASE}/{event_type}/{month:02d}/{day:02d}"
        
        logger.info(f"Fetching from: {url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully fetched data for {month}/{day}, type: {event_type}")
            return data
            
    except Exception as e:
        logger.error(f"Error fetching historical events: {e}")
        return {}


def format_historical_event(event: dict) -> str:
    """Format a historical event for display."""
    year = event.get("year", "Unknown")
    text = event.get("text", "No description available")
    
    # Get Wikipedia links if available
    links = event.get("pages", [])
    wikipedia_links = []
    if links:
        for link in links[:2]:  # Limit to first 2 links
            title = link.get("displaytitle", link.get("title", ""))
            if title:
                wikipedia_links.append(f"[{title}](https://en.wikipedia.org/wiki/{link.get('title', '').replace(' ', '_')})")
    
    formatted = f"**{year}**: {text}"
    if wikipedia_links:
        formatted += f"\n*Related: {', '.join(wikipedia_links)}*"
    
    return formatted


def format_birth_death_event(event: dict, event_type: str) -> str:
    """Format a birth/death event for display."""
    year = event.get("year", "Unknown")
    text = event.get("text", "No description available")
    
    # Get Wikipedia links if available
    links = event.get("pages", [])
    wikipedia_links = []
    if links:
        for link in links[:1]:  # Limit to first link for births/deaths
            title = link.get("displaytitle", link.get("title", ""))
            if title:
                wikipedia_links.append(f"[{title}](https://en.wikipedia.org/wiki/{link.get('title', '').replace(' ', '_')})")
    
    icon = "🎂" if event_type == "births" else "⚰️"
    formatted = f"**{year}**: {text} {icon}"
    
    if wikipedia_links:
        formatted += f"\n*Learn more: {', '.join(wikipedia_links)}*"
    
    return formatted


async def process_mcp_tool_call(tool_name: str, arguments: dict) -> list:
    """Process MCP tool calls and return results."""
    try:
        if tool_name == "get_historical_facts":
            month = arguments["month"]
            day = arguments["day"]
            event_type = arguments.get("event_type", "all")
            
            data = await fetch_historical_events(month, day, event_type)
            
            response_parts = []
            response_parts.append(f"# Historical Facts for {month}/{day}")
            response_parts.append("")
            
            if event_type == "all":
                # Show a summary of all types
                if "events" in data and data["events"]:
                    response_parts.append("## 📅 Historical Events")
                    for event in data["events"][:3]:  
                        response_parts.append(format_historical_event(event))
                        response_parts.append("")
                
                if "births" in data and data["births"]:
                    response_parts.append("## 🎂 Notable Births")
                    for birth in data["births"][:2]:  
                        response_parts.append(format_birth_death_event(birth, "births"))
                        response_parts.append("")
                
                if "deaths" in data and data["deaths"]:
                    response_parts.append("## ⚰️ Notable Deaths")
                    for death in data["deaths"][:2]:  
                        response_parts.append(format_birth_death_event(death, "deaths"))
                        response_parts.append("")
            else:
                if event_type in data and data[event_type]:
                    event_title = {
                        "events": "📅 Historical Events",
                        "births": "🎂 Notable Births", 
                        "deaths": "⚰️ Notable Deaths",
                        "holidays": "🎉 Holidays & Observances"
                    }.get(event_type, "Historical Facts")
                    
                    response_parts.append(f"## {event_title}")
                    
                    for event in data[event_type][:5]:
                        if event_type in ["births", "deaths"]:
                            response_parts.append(format_birth_death_event(event, event_type))
                        else:
                            response_parts.append(format_historical_event(event))
                        response_parts.append("")
                else:
                    response_parts.append(f"No {event_type} found for {month}/{day}.")
            
            return [{"type": "text", "text": "\n".join(response_parts)}]
        
        elif tool_name == "get_todays_historical_facts":
            today = date.today()
            month = today.month
            day = today.day
            event_type = arguments.get("event_type", "all")
            
            data = await fetch_historical_events(month, day, event_type)
            
            response_parts = []
            response_parts.append(f"# Today in History ({month}/{day})")
            response_parts.append("")
            
            if event_type == "all":
                # Show a summary of all types
                if "events" in data and data["events"]:
                    response_parts.append("## 📅 Historical Events")
                    for event in data["events"][:3]:  
                        response_parts.append(format_historical_event(event))
                        response_parts.append("")
                
                if "births" in data and data["births"]:
                    response_parts.append("## 🎂 Notable Births")
                    for birth in data["births"][:2]:  
                        response_parts.append(format_birth_death_event(birth, "births"))
                        response_parts.append("")
                
                if "deaths" in data and data["deaths"]:
                    response_parts.append("## ⚰️ Notable Deaths")
                    for death in data["deaths"][:2]:  
                        response_parts.append(format_birth_death_event(death, "deaths"))
                        response_parts.append("")
            else:
                if event_type in data and data[event_type]:
                    event_title = {
                        "events": "📅 Historical Events",
                        "births": "🎂 Notable Births", 
                        "deaths": "⚰️ Notable Deaths",
                        "holidays": "🎉 Holidays & Observances"
                    }.get(event_type, "Historical Facts")
                    
                    response_parts.append(f"## {event_title}")
                    
                    for event in data[event_type][:5]:
                        if event_type in ["births", "deaths"]:
                            response_parts.append(format_birth_death_event(event, event_type))
                        else:
                            response_parts.append(format_historical_event(event))
                        response_parts.append("")
                else:
                    response_parts.append(f"No {event_type} found for today.")
            
            return [{"type": "text", "text": "\n".join(response_parts)}]
        
        elif tool_name == "get_random_historical_fact":
            import random
            
            # Generate random date
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Use 28 to avoid invalid dates
            
            event_type = arguments.get("event_type", "events")
            
            data = await fetch_historical_events(month, day, event_type)
            
            response_parts = []
            response_parts.append(f"# Random Historical Fact ({month}/{day})")
            response_parts.append("")
            
            if event_type in data and data[event_type]:
                # Pick a random event from the results
                random_event = random.choice(data[event_type])
                
                event_title = {
                    "events": "📅 Random Historical Event",
                    "births": "🎂 Random Birth", 
                    "deaths": "⚰️ Random Death",
                    "holidays": "🎉 Random Holiday"
                }.get(event_type, "Random Historical Fact")
                
                response_parts.append(f"## {event_title}")
                
                if event_type in ["births", "deaths"]:
                    response_parts.append(format_birth_death_event(random_event, event_type))
                else:
                    response_parts.append(format_historical_event(random_event))
            else:
                response_parts.append(f"No {event_type} found for {month}/{day}.")
            
            return [{"type": "text", "text": "\n".join(response_parts)}]
        
        else:
            return [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
    
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]


async def process_mcp_request(request_data: Dict) -> Dict:
    """Process MCP request using JSON-RPC protocol."""
    try:
        # Convert request to JSON-RPC format if needed
        if "jsonrpc" not in request_data:
            request_data = {
                "jsonrpc": "2.0",
                "id": request_data.get("id", 1),
                "method": request_data.get("method"),
                "params": request_data.get("params", {})
            }
        
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id", 1)
        
        logger.info(f"Processing MCP method: {method}")
        
        # Handle different MCP methods
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "historical-facts-mcp",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "notifications/initialized":
            # Client notifies server that initialization is complete
            logger.info("Client initialization complete")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
            
        elif method == "tools/list":
            tools = [
                {
                    "name": "get_historical_facts",
                    "description": "Get historical facts for a specific date (month/day). Returns events, births, deaths, and holidays that occurred on this date throughout history.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "month": {
                                "type": "integer",
                                "description": "Month (1-12)",
                                "minimum": 1,
                                "maximum": 12
                            },
                            "day": {
                                "type": "integer", 
                                "description": "Day (1-31)",
                                "minimum": 1,
                                "maximum": 31
                            },
                            "event_type": {
                                "type": "string",
                                "description": "Type of events to get",
                                "enum": ["events", "births", "deaths", "holidays", "all"],
                                "default": "all"
                            }
                        },
                        "required": ["month", "day"]
                    }
                },
                {
                    "name": "get_todays_historical_facts",
                    "description": "Get historical facts for today's date. Shows what happened on this day in history across different years.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "event_type": {
                                "type": "string",
                                "description": "Type of events to get",
                                "enum": ["events", "births", "deaths", "holidays", "all"],
                                "default": "all"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_random_historical_fact",
                    "description": "Get a random historical fact from a random date in history. Perfect for discovering surprising historical events!",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "event_type": {
                                "type": "string",
                                "description": "Type of event to get",
                                "enum": ["events", "births", "deaths", "holidays"],
                                "default": "events"
                            }
                        },
                        "required": []
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
            
        elif method == "resources/list":
            # Return empty resources list (we don't provide any resources)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": []
                }
            }
            
        elif method == "resources/read":
            # Resources read method (not applicable for our server)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "Resources/read not supported - this server only provides tools"
                }
            }
            
        elif method == "prompts/list":
            # Return empty prompts list (we don't provide any prompts)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": []
                }
            }
            
        elif method == "tools/call":
            # Call tool
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            result = await process_mcp_tool_call(tool_name, tool_args)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id, 
                "result": {
                    "content": result
                }
            }
            
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return {
            "jsonrpc": "2.0", 
            "id": request_data.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI app."""
    logger.info("Starting Historical Facts MCP HTTP Server...")
    yield
    logger.info("Shutting down Historical Facts MCP HTTP Server...")


app = FastAPI(
    title="Historical Facts MCP Server",
    description="HTTP server with both REST API and MCP protocol support for ChatGPT Desktop integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MCP Endpoints
@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests from ChatGPT Desktop."""
    try:
        body = await request.body()
        request_data = json.loads(body)
        
        logger.info(f"MCP request: {request_data}")
        
        # Process the MCP request
        response = await process_mcp_request(request_data)
        
        logger.info(f"MCP response: {response}")
        
        return JSONResponse(content=response)
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0", 
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )


# REST API Endpoints (existing functionality)
@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Historical Facts MCP Server",
        "description": "HTTP server with REST API and MCP protocol support",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp (for ChatGPT Desktop)",
            "rest_api": {
                "health": "/health",
                "today": "/historical-facts/today", 
                "date": "/historical-facts/{month}/{day}",
                "random": "/historical-facts/random",
                "docs": "/docs"
            }
        },
        "protocols": ["http", "mcp"],
        "capabilities": ["tools", "historical_facts"],
        "tools": [
            "get_historical_facts",
            "get_todays_historical_facts",
            "get_random_historical_fact"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/historical-facts/today")
async def get_today_facts(event_type: str = "all"):
    """Get historical facts for today."""
    today = date.today()
    data = await fetch_historical_events(today.month, today.day, event_type)
    
    return {
        "date": f"{today.month}/{today.day}",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/historical-facts/{month}/{day}")
async def get_historical_facts(month: int, day: int, event_type: str = "all"):
    """Get historical facts for a specific date."""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if day < 1 or day > 31:
        raise HTTPException(status_code=400, detail="Day must be between 1 and 31")
    
    data = await fetch_historical_events(month, day, event_type)
    
    return {
        "date": f"{month}/{day}",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/historical-facts/random")
async def get_random_fact(event_type: str = "events"):
    """Get a random historical fact."""
    import random
    
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Use 28 to avoid invalid dates
    
    data = await fetch_historical_events(month, day, event_type)
    
    return {
        "date": f"{month}/{day}",
        "data": data,
        "random": True,
        "timestamp": datetime.now().isoformat()
    }


async def main():
    """Main entry point."""
    logger.info("Starting Historical Facts MCP HTTP Server with /mcp endpoint...")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0", 
        port=8003,  # New port to avoid conflict
        log_level="info"
    )
    
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    asyncio.run(main())
