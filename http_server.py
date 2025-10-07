#!/usr/bin/env python3
"""
HTTP wrapper for the Historical Facts MCP Server

This creates an HTTP interface around the MCP server so it can be accessed
externally and integrated with web-based AI applications.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historical-facts-http")

app = FastAPI(
    title="Historical Facts MCP Server",
    description="A fun API that provides historical facts from events that happened on the same date in history",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wikipedia On This Day API base URL
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"


async def fetch_historical_events(month: int, day: int, event_type: str = "all") -> dict:
    """Fetch historical events from Wikipedia's On This Day API"""
    url = f"{WIKI_API_BASE}/{event_type}/{month:02d}/{day:02d}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching data from Wikipedia API: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


def format_historical_event(event: dict) -> dict:
    """Format a single historical event for API response"""
    text = event.get('text', 'No description available')
    year = event.get('year', 'Unknown year')
    
    # Get additional context from pages if available
    pages = event.get('pages', [])
    formatted_event = {
        "year": year,
        "text": text,
        "pages": []
    }
    
    if pages:
        for page in pages[:1]:  # Limit to first page for performance
            page_info = {
                "title": page.get('displaytitle', page.get('title', '')),
                "extract": page.get('extract', '')[:300] + "..." if page.get('extract') and len(page.get('extract', '')) > 300 else page.get('extract', ''),
                "url": page.get('content_urls', {}).get('desktop', {}).get('page', ''),
                "thumbnail": page.get('thumbnail', {}).get('source', '') if page.get('thumbnail') else ''
            }
            formatted_event["pages"].append(page_info)
    
    return formatted_event


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with basic information"""
    return {
        "name": "Historical Facts MCP Server",
        "version": "1.0.0",
        "description": "A fun API that provides historical facts from events that happened on the same date in history",
        "endpoints": [
            "/historical-facts/{month}/{day}",
            "/historical-facts/today",
            "/historical-facts/random",
            "/docs"
        ],
        "github": "https://github.com/oscar-fern-labs/historical-facts-mcp-server"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/historical-facts/{month}/{day}", tags=["Historical Facts"])
async def get_historical_facts(
    month: int,
    day: int,
    event_type: str = "all"
):
    """
    Get historical facts for a specific date
    
    - **month**: Month (1-12)
    - **day**: Day (1-31)
    - **event_type**: Type of events ("all", "events", "births", "deaths", "holidays")
    """
    # Validate inputs
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    if not (1 <= day <= 31):
        raise HTTPException(status_code=400, detail="Day must be between 1 and 31")
    
    if event_type not in ["all", "events", "births", "deaths", "holidays"]:
        raise HTTPException(status_code=400, detail="event_type must be one of: all, events, births, deaths, holidays")
    
    # Validate date exists
    try:
        from datetime import date
        date(2024, month, day)  # Use 2024 as it's a leap year
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {month}/{day}")
    
    data = await fetch_historical_events(month, day, event_type)
    
    # Format the response
    response = {
        "date": f"{month:02d}/{day:02d}",
        "event_types": []
    }
    
    if event_type == "all":
        for category in ["events", "births", "deaths", "holidays"]:
            if category in data and data[category]:
                formatted_events = []
                for event in data[category][:5]:  # Limit to 5 events per category
                    formatted_events.append(format_historical_event(event))
                
                response["event_types"].append({
                    "type": category,
                    "count": len(data[category]),
                    "events": formatted_events
                })
    else:
        if event_type in data and data[event_type]:
            formatted_events = []
            for event in data[event_type][:10]:  # Allow more events for specific type
                formatted_events.append(format_historical_event(event))
            
            response["event_types"].append({
                "type": event_type,
                "count": len(data[event_type]),
                "events": formatted_events
            })
    
    return response


@app.get("/historical-facts/today", tags=["Historical Facts"])
async def get_todays_historical_facts(event_type: str = "all"):
    """
    Get historical facts for today's date
    
    - **event_type**: Type of events ("all", "events", "births", "deaths", "holidays")
    """
    today = datetime.now()
    return await get_historical_facts(today.month, today.day, event_type)


@app.get("/historical-facts/random", tags=["Historical Facts"])
async def get_random_historical_fact(event_type: str = "events"):
    """
    Get a random historical fact from a random date
    
    - **event_type**: Type of events ("events", "births", "deaths", "holidays")
    """
    import random
    
    # Generate random date
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Use 28 to avoid invalid dates
    
    if event_type not in ["events", "births", "deaths", "holidays"]:
        raise HTTPException(status_code=400, detail="event_type must be one of: events, births, deaths, holidays")
    
    data = await fetch_historical_events(month, day, event_type)
    
    if event_type in data and data[event_type]:
        # Pick a random event
        random_event = random.choice(data[event_type])
        
        return {
            "date": f"{month:02d}/{day:02d}",
            "event_type": event_type,
            "fact": format_historical_event(random_event)
        }
    else:
        # Try a different date if no events found
        return {
            "date": f"{month:02d}/{day:02d}",
            "event_type": event_type,
            "error": f"No {event_type} found for {month}/{day}. Please try again."
        }


# MCP-compatible endpoint for tool integration
@app.post("/mcp/call-tool", tags=["MCP"])
async def mcp_call_tool(request: Dict[str, Any]):
    """
    MCP-compatible endpoint for tool calls
    
    This endpoint mimics the MCP protocol for easier integration with AI applications
    """
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    try:
        if tool_name == "get_historical_facts":
            month = arguments.get("month")
            day = arguments.get("day")
            event_type = arguments.get("event_type", "all")
            
            if not month or not day:
                return {"error": "Both month and day are required parameters"}
            
            result = await get_historical_facts(month, day, event_type)
            return {"result": result}
        
        elif tool_name == "get_todays_historical_facts":
            event_type = arguments.get("event_type", "all")
            result = await get_todays_historical_facts(event_type)
            return {"result": result}
        
        elif tool_name == "get_random_historical_fact":
            event_type = arguments.get("event_type", "events")
            result = await get_random_historical_fact(event_type)
            return {"result": result}
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
