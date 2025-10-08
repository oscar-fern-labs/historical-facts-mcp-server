#!/usr/bin/env python3
"""
Enhanced Historical Facts MCP Server for Apps SDK Demo

This server showcases the full OpenAI Apps SDK capabilities including:
- Rich interactive UI components
- Persistent state management
- Interactive timelines and carousels
- Beautiful visual cards with metadata
- Geographic event mapping
- Discovery features and recommendations

Author: vigorous_bohr
License: MIT
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import httpx
from contextlib import asynccontextmanager
import random
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Wikipedia On This Day API base URL
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historical-facts-apps-sdk")

# Global state for demo (in production, use proper database)
user_favorites = []
user_preferences = {
    "preferred_categories": ["events", "births"],
    "discovery_mode": "chronological"
}

async def fetch_historical_events(month: int, day: int, event_type: str = "all") -> dict:
    """Fetch historical events from Wikipedia's On This Day API with enhanced metadata"""
    try:
        if event_type == "all":
            url = f"{WIKI_API_BASE}/all/{month:02d}/{day:02d}"
        else:
            url = f"{WIKI_API_BASE}/{event_type}/{month:02d}/{day:02d}"
        
        logger.info(f"Fetching from: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Enhance data with Apps SDK metadata
            enhanced_data = enhance_historical_data(data, month, day)
            return enhanced_data
            
    except Exception as e:
        logger.error(f"Error fetching historical events: {e}")
        return {"error": str(e), "events": [], "births": [], "deaths": [], "holidays": []}

def enhance_historical_data(data: dict, month: int, day: int) -> dict:
    """Enhance historical data with Apps SDK specific metadata"""
    enhanced = data.copy()
    
    # Add rich metadata for each event type
    for category in ["events", "births", "deaths", "holidays"]:
        if category in enhanced:
            for item in enhanced[category]:
                # Add unique ID for state management
                item["id"] = str(uuid.uuid4())
                
                # Add Apps SDK specific metadata
                item["category"] = category
                item["date_info"] = {
                    "month": month,
                    "day": day,
                    "formatted": f"{month:02d}/{day:02d}"
                }
                
                # Add interaction metadata
                item["is_favorite"] = item["id"] in user_favorites
                item["interaction_count"] = 0
                
                # Enhanced descriptions for better UI
                if "text" in item:
                    item["enhanced_description"] = enhance_description(item["text"], item.get("year"))
                
                # Add geographic data if available
                if "pages" in item and len(item["pages"]) > 0:
                    page = item["pages"][0]
                    item["primary_page"] = {
                        "title": page.get("title", ""),
                        "extract": page.get("extract", "")[:200] + "..." if page.get("extract", "") else "",
                        "thumbnail": page.get("thumbnail", {}),
                        "content_urls": page.get("content_urls", {})
                    }
    
    # Add discovery recommendations
    enhanced["recommendations"] = generate_recommendations(enhanced, month, day)
    
    # Add Apps SDK component metadata
    enhanced["component_metadata"] = {
        "total_events": len(enhanced.get("events", [])),
        "total_births": len(enhanced.get("births", [])),
        "total_deaths": len(enhanced.get("deaths", [])),
        "total_holidays": len(enhanced.get("holidays", [])),
        "date_formatted": f"{datetime(2024, month, day).strftime('%B %d')}",
        "has_images": any(
            item.get("primary_page", {}).get("thumbnail")
            for category in ["events", "births", "deaths", "holidays"]
            for item in enhanced.get(category, [])
        )
    }
    
    return enhanced

def enhance_description(text: str, year: Optional[int]) -> dict:
    """Create enhanced description with Apps SDK metadata"""
    return {
        "summary": text[:150] + "..." if len(text) > 150 else text,
        "full_text": text,
        "year": year,
        "era": get_historical_era(year) if year else None,
        "time_ago": get_time_ago(year) if year else None
    }

def get_historical_era(year: int) -> str:
    """Get historical era for better categorization"""
    if year >= 2000:
        return "21st Century"
    elif year >= 1900:
        return "20th Century"
    elif year >= 1800:
        return "19th Century"
    elif year >= 1700:
        return "18th Century"
    elif year >= 1600:
        return "17th Century"
    elif year >= 1500:
        return "16th Century"
    elif year >= 1000:
        return "Medieval Period"
    else:
        return "Ancient Times"

def get_time_ago(year: int) -> str:
    """Get human-readable time ago"""
    current_year = datetime.now().year
    years_ago = current_year - year
    
    if years_ago < 10:
        return f"{years_ago} years ago"
    elif years_ago < 100:
        return f"{years_ago // 10 * 10}+ years ago"
    elif years_ago < 1000:
        return f"{years_ago // 100} centuries ago"
    else:
        return f"{years_ago // 1000}+ millennia ago"

def generate_recommendations(data: dict, month: int, day: int) -> dict:
    """Generate discovery recommendations for Apps SDK carousel"""
    recommendations = {
        "related_dates": [
            {"month": month, "day": (day + i) % 31 + 1, "reason": f"{i} days later"}
            for i in [1, 7, 30]
        ],
        "same_month_highlights": [
            {"month": month, "day": day + 10, "reason": "Major events this month"}
            for day in [1, 15]
            if day != day
        ][:2],
        "historical_anniversaries": [
            {"month": month, "day": day, "year_offset": offset, "reason": f"{offset} years ago"}
            for offset in [10, 25, 50, 100]
        ]
    }
    
    # Add category-based recommendations
    categories = ["events", "births", "deaths"]
    for category in categories:
        if category in data and data[category]:
            # Pick interesting items for recommendations
            items = data[category][:3]  # Top 3 items
            recommendations[f"similar_{category}"] = [
                {
                    "id": item.get("id"),
                    "title": item.get("text", "")[:50] + "...",
                    "reason": f"More {category.replace('_', ' ')}"
                }
                for item in items
            ]
    
    return recommendations

# FastAPI app setup
app = FastAPI(title="Historical Facts Apps SDK Server", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for UI components
app.mount("/static", StaticFiles(directory="ui_components"), name="static")

# Resource endpoints for MCP
@app.get("/resources/{resource_name}")
async def get_resource(resource_name: str):
    """Serve MCP UI resources"""
    try:
        if resource_name == "historical-timeline.html":
            return FileResponse("ui_components/historical-timeline.html", media_type="text/html+skybridge")
        elif resource_name == "historical-discovery.html":
            return FileResponse("ui_components/historical-discovery.html", media_type="text/html+skybridge")
        elif resource_name == "historical-map.html":
            return FileResponse("ui_components/historical-map.html", media_type="text/html+skybridge")
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logger.error(f"Error serving resource {resource_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with Apps SDK information"""
    return {
        "service": "Historical Facts Apps SDK Server",
        "version": "2.0.0",
        "description": "Enhanced MCP server showcasing OpenAI Apps SDK capabilities",
        "features": [
            "Interactive Timeline Components",
            "Rich Historical Event Cards",
            "Geographic Event Mapping",
            "Discovery Carousel",
            "Favorites System",
            "Smart Filtering with State Persistence",
            "Theme-aware UI Components"
        ],
        "endpoints": {
            "mcp": "/mcp",
            "ui_components": "/static/",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# MCP Protocol Implementation
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Enhanced MCP endpoint with Apps SDK support"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        
        logger.info(f"MCP Request - Method: {method}, Params: {params}")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "historical-facts-apps-sdk",
                        "version": "2.0.0",
                        "description": "Enhanced Historical Facts MCP Server with Apps SDK components"
                    }
                }
            }
            
        elif method == "notifications/initialized":
            response = {"jsonrpc": "2.0", "id": body.get("id"), "result": {}}
            
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "historical_timeline",
                            "description": "Display an interactive timeline of historical events with rich UI components",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "month": {"type": "integer", "minimum": 1, "maximum": 12},
                                    "day": {"type": "integer", "minimum": 1, "maximum": 31},
                                    "event_type": {
                                        "type": "string", 
                                        "enum": ["all", "events", "births", "deaths", "holidays"],
                                        "default": "all"
                                    }
                                },
                                "required": ["month", "day"]
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-timeline.html",
                                "openai/toolInvocation/invoking": "Crafting a historical timeline",
                                "openai/toolInvocation/invoked": "Timeline ready for exploration"
                            }
                        },
                        {
                            "name": "historical_discovery",
                            "description": "Discover historical events with interactive cards and recommendations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "discovery_type": {
                                        "type": "string",
                                        "enum": ["random", "today", "recommended", "favorites"],
                                        "default": "random"
                                    },
                                    "category_filter": {
                                        "type": "string",
                                        "enum": ["all", "events", "births", "deaths", "holidays"],
                                        "default": "all"
                                    }
                                }
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-discovery.html", 
                                "openai/toolInvocation/invoking": "Exploring historical discoveries",
                                "openai/toolInvocation/invoked": "Found fascinating historical moments"
                            }
                        },
                        {
                            "name": "historical_map",
                            "description": "Interactive map showing geographic locations of historical events",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "month": {"type": "integer", "minimum": 1, "maximum": 12},
                                    "day": {"type": "integer", "minimum": 1, "maximum": 31},
                                    "map_type": {
                                        "type": "string",
                                        "enum": ["world", "events_only", "births_deaths"],
                                        "default": "world"
                                    }
                                },
                                "required": ["month", "day"]
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-map.html",
                                "openai/toolInvocation/invoking": "Mapping historical locations",
                                "openai/toolInvocation/invoked": "Historical map rendered"
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "historical_timeline":
                month = arguments.get("month")
                day = arguments.get("day")
                event_type = arguments.get("event_type", "all")
                
                data = await fetch_historical_events(month, day, event_type)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Historical timeline for {month:02d}/{day:02d} with {len(data.get('events', []))} events, {len(data.get('births', []))} births, and {len(data.get('deaths', []))} deaths."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_timeline",
                            "data": data,
                            "metadata": {
                                "date": f"{month:02d}/{day:02d}",
                                "event_type": event_type,
                                "component_type": "interactive_timeline"
                            }
                        }
                    }
                }
                
            elif tool_name == "historical_discovery":
                discovery_type = arguments.get("discovery_type", "random")
                category_filter = arguments.get("category_filter", "all")
                
                if discovery_type == "today":
                    today = datetime.now()
                    month, day = today.month, today.day
                elif discovery_type == "random":
                    month, day = random.randint(1, 12), random.randint(1, 28)
                else:
                    # Default to today for other types
                    today = datetime.now()
                    month, day = today.month, today.day
                
                data = await fetch_historical_events(month, day, category_filter)
                
                response = {
                    "jsonrpc": "2.0", 
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Historical discovery for {month:02d}/{day:02d} - found {sum(len(data.get(k, [])) for k in ['events', 'births', 'deaths', 'holidays'])} historical items."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_discovery",
                            "data": data,
                            "metadata": {
                                "discovery_type": discovery_type,
                                "category_filter": category_filter,
                                "component_type": "discovery_cards"
                            }
                        }
                    }
                }
                
            elif tool_name == "historical_map":
                month = arguments.get("month")
                day = arguments.get("day")
                map_type = arguments.get("map_type", "world")
                
                data = await fetch_historical_events(month, day, "all")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"), 
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Historical map for {month:02d}/{day:02d} showing geographic distribution of historical events."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_map",
                            "data": data,
                            "metadata": {
                                "date": f"{month:02d}/{day:02d}",
                                "map_type": map_type,
                                "component_type": "interactive_map"
                            }
                        }
                    }
                }
                
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
                
        elif method == "resources/list":
            base_url = "https://apps-sdk-server-morphvm-87kmb6bw.http.cloud.morph.so"
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "resources": [
                        {
                            "uri": "ui://widget/historical-timeline.html",
                            "name": "Historical Timeline Component",
                            "description": "Interactive timeline UI component",
                            "mimeType": "text/html+skybridge"
                        },
                        {
                            "uri": "ui://widget/historical-discovery.html", 
                            "name": "Historical Discovery Component",
                            "description": "Discovery cards UI component",
                            "mimeType": "text/html+skybridge"
                        },
                        {
                            "uri": "ui://widget/historical-map.html",
                            "name": "Historical Map Component", 
                            "description": "Interactive map UI component",
                            "mimeType": "text/html+skybridge"
                        }
                    ]
                }
            }
            
        elif method == "resources/read":
            uri = params.get("uri")
            if uri == "ui://widget/historical-timeline.html":
                with open("ui_components/historical-timeline.html", "r") as f:
                    content = f.read()
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/html+skybridge",
                                "text": content
                            }
                        ]
                    }
                }
            elif uri == "ui://widget/historical-discovery.html":
                with open("ui_components/historical-discovery.html", "r") as f:
                    content = f.read()
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/html+skybridge",
                                "text": content
                            }
                        ]
                    }
                }
            elif uri == "ui://widget/historical-map.html":
                with open("ui_components/historical-map.html", "r") as f:
                    content = f.read()
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/html+skybridge",
                                "text": content
                            }
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32602, "message": f"Resource not found: {uri}"}
                }
            
        elif method == "prompts/list":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"prompts": []}
            }
            
        else:
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
            
        logger.info(f"MCP Response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"MCP error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if body else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
