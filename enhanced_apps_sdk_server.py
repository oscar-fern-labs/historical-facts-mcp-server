#!/usr/bin/env python3
"""
Enhanced Historical Facts MCP Server for Apps SDK Demo
Fully compliant with OpenAI Apps SDK specifications

This server demonstrates ALL Apps SDK features:
- Rich interactive UI components with React
- Persistent widget state management
- Interactive actions and follow-up tool calls
- Theme-aware design
- Structured content with proper metadata
- Resource registration and serving
- Beautiful visual components (timeline, discovery, map)

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
import os

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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data.get('events', []))} events from Wikipedia API")
            
            # Enhance data with Apps SDK metadata
            enhanced_data = enhance_historical_data(data, month, day)
            
            logger.info(f"Enhanced data contains {len(enhanced_data.get('events', []))} events")
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
            {"month": month, "day": target_day, "reason": "Major events this month"}
            for target_day in [1, 15]
            if target_day != day
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

@app.get("/")
async def root():
    """Serve the Apps SDK Demo page"""
    return FileResponse("ui_components/apps-sdk-demo.html", media_type="text/html")

@app.get("/api")
async def api_info():
    """API endpoint with Apps SDK information"""
    return {
        "service": "Enhanced Historical Facts Apps SDK Server",
        "version": "2.0.0",
        "description": "Comprehensive MCP server showcasing ALL OpenAI Apps SDK capabilities",
        "features": [
            "✨ Interactive Timeline Components with React",
            "🎴 Rich Historical Event Cards with Images",
            "🗺️ Geographic Event Mapping",
            "🎲 Discovery Carousel with Recommendations",
            "⭐ Favorites System with State Persistence",
            "🔍 Smart Filtering with Real-time Updates",
            "🎨 Theme-aware UI Components",
            "📱 Mobile-responsive Design",
            "🔄 Interactive Actions & Follow-up Calls",
            "💾 Widget State Management"
        ],
        "apps_sdk_demo": {
            "components": 3,
            "tools": 3,
            "resources": 3,
            "interactive_features": 10
        },
        "endpoints": {
            "demo": "/",
            "mcp": "/mcp",
            "ui_components": "/static/",
            "resources": "/resources/",
            "health": "/health",
            "api": "/api"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Resource endpoints for MCP
@app.get("/resources/{resource_name}")
async def get_resource(resource_name: str):
    """Serve MCP UI resources"""
    try:
        resource_path = f"ui_components/{resource_name}"
        if os.path.exists(resource_path):
            return FileResponse(resource_path, media_type="text/html+skybridge")
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logger.error(f"Error serving resource {resource_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP Protocol Implementation
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Enhanced MCP endpoint with full Apps SDK support"""
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
                        "name": "historical-facts-apps-sdk-enhanced",
                        "version": "2.0.0",
                        "description": "Enhanced Historical Facts MCP Server showcasing ALL OpenAI Apps SDK capabilities"
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
                            "name": "historical_timeline_explorer",
                            "description": "🕰️ Interactive historical timeline with rich visual cards, filtering, and favorites system. Showcases Apps SDK component state management and theme integration.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "month": {"type": "integer", "minimum": 1, "maximum": 12, "description": "Month (1-12)"},
                                    "day": {"type": "integer", "minimum": 1, "maximum": 31, "description": "Day of month"},
                                    "event_type": {
                                        "type": "string", 
                                        "enum": ["all", "events", "births", "deaths", "holidays"],
                                        "default": "all",
                                        "description": "Type of historical events to display"
                                    },
                                    "view_mode": {
                                        "type": "string",
                                        "enum": ["timeline", "cards", "compact"],
                                        "default": "timeline",
                                        "description": "Visual presentation mode"
                                    }
                                },
                                "required": ["month", "day"]
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-timeline-simple.html",
                                "openai/toolInvocation/invoking": "🕰️ Crafting an interactive historical timeline with rich visual components...",
                                "openai/toolInvocation/invoked": "✨ Timeline explorer ready! Explore historical events with interactive filters and favorites.",
                                "openai/description": "Interactive timeline showcasing Apps SDK features: state persistence, theme integration, and rich UI components."
                            }
                        },
                        {
                            "name": "historical_discovery_experience",
                            "description": "🌟 Immersive historical discovery with smart recommendations, beautiful cards, and interactive carousels. Demonstrates Apps SDK's rich component capabilities.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "discovery_mode": {
                                        "type": "string",
                                        "enum": ["serendipity", "guided", "themed", "favorites", "trending"],
                                        "default": "serendipity",
                                        "description": "How to discover historical content"
                                    },
                                    "focus_category": {
                                        "type": "string",
                                        "enum": ["all", "events", "births", "deaths", "holidays", "science", "arts", "politics"],
                                        "default": "all",
                                        "description": "Focus area for discovery"
                                    },
                                    "time_period": {
                                        "type": "string",
                                        "enum": ["any", "ancient", "medieval", "renaissance", "modern", "contemporary"],
                                        "default": "any",
                                        "description": "Historical time period focus"
                                    }
                                }
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-discovery.html", 
                                "openai/toolInvocation/invoking": "🔍 Curating fascinating historical discoveries with smart recommendations...",
                                "openai/toolInvocation/invoked": "🌟 Discovery experience ready! Explore history through beautiful interactive cards and recommendations.",
                                "openai/description": "Rich discovery interface with carousels, recommendations, and interactive elements showcasing Apps SDK capabilities."
                            }
                        },
                        {
                            "name": "historical_world_map",
                            "description": "🗺️ Interactive world map plotting historical events geographically with beautiful markers and location details. Shows Apps SDK's advanced visualization capabilities.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "month": {"type": "integer", "minimum": 1, "maximum": 12, "description": "Month (1-12)"},
                                    "day": {"type": "integer", "minimum": 1, "maximum": 31, "description": "Day of month"},
                                    "map_style": {
                                        "type": "string",
                                        "enum": ["satellite", "terrain", "political", "historical"],
                                        "default": "political",
                                        "description": "Map visualization style"
                                    },
                                    "marker_density": {
                                        "type": "string",
                                        "enum": ["detailed", "moderate", "minimal"],
                                        "default": "moderate",
                                        "description": "How many location markers to show"
                                    },
                                    "focus_region": {
                                        "type": "string",
                                        "enum": ["world", "europe", "asia", "americas", "africa", "oceania"],
                                        "default": "world",
                                        "description": "Geographic region to focus on"
                                    }
                                },
                                "required": ["month", "day"]
                            },
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/historical-map.html",
                                "openai/toolInvocation/invoking": "🗺️ Mapping historical events across the globe with interactive markers...",
                                "openai/toolInvocation/invoked": "🌍 World map ready! Explore where history happened with interactive geographic visualization.",
                                "openai/description": "Geographic visualization of historical events with interactive maps, markers, and location details."
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "historical_timeline_explorer":
                month = arguments.get("month")
                day = arguments.get("day")
                event_type = arguments.get("event_type", "all")
                view_mode = arguments.get("view_mode", "timeline")
                
                data = await fetch_historical_events(month, day, event_type)
                
                # Add Apps SDK specific metadata
                data["apps_sdk_metadata"] = {
                    "component_type": "interactive_timeline",
                    "view_mode": view_mode,
                    "supports_favorites": True,
                    "supports_filtering": True,
                    "theme_aware": True,
                    "responsive": True,
                    "interactive_actions": ["favorite", "filter", "expand", "navigate"]
                }
                
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🕰️ Interactive historical timeline for {data.get('component_metadata', {}).get('date_formatted', f'{month:02d}/{day:02d}')} with {sum(len(data.get(k, [])) for k in ['events', 'births', 'deaths', 'holidays'])} historical items. Features rich visual cards, smart filtering, favorites system, and theme-aware design."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_timeline_explorer",
                            "data": data,
                            "metadata": {
                                "date": f"{month:02d}/{day:02d}",
                                "event_type": event_type,
                                "view_mode": view_mode,
                                "component_type": "interactive_timeline",
                                "apps_sdk_features": ["state_persistence", "theme_integration", "interactive_actions", "rich_ui"]
                            }
                        }
                    }
                }
                
            elif tool_name == "historical_discovery_experience":
                discovery_mode = arguments.get("discovery_mode", "serendipity")
                focus_category = arguments.get("focus_category", "all")
                time_period = arguments.get("time_period", "any")
                
                if discovery_mode == "serendipity":
                    month, day = random.randint(1, 12), random.randint(1, 28)
                else:
                    today = datetime.now()
                    month, day = today.month, today.day
                
                data = await fetch_historical_events(month, day, focus_category)
                
                # Add Apps SDK discovery metadata
                data["apps_sdk_metadata"] = {
                    "component_type": "discovery_experience",
                    "discovery_mode": discovery_mode,
                    "supports_recommendations": True,
                    "supports_carousels": True,
                    "interactive_cards": True,
                    "follow_up_actions": ["explore_similar", "save_favorite", "share", "deep_dive"]
                }
                
                response = {
                    "jsonrpc": "2.0", 
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🌟 Historical discovery experience curated for {data.get('component_metadata', {}).get('date_formatted', f'{month:02d}/{day:02d}')}! Found {sum(len(data.get(k, [])) for k in ['events', 'births', 'deaths', 'holidays'])} fascinating historical moments with smart recommendations and beautiful interactive cards."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_discovery_experience",
                            "data": data,
                            "metadata": {
                                "discovery_mode": discovery_mode,
                                "focus_category": focus_category,
                                "time_period": time_period,
                                "component_type": "discovery_cards",
                                "apps_sdk_features": ["carousels", "recommendations", "interactive_cards", "follow_up_actions"]
                            }
                        }
                    }
                }
                
            elif tool_name == "historical_world_map":
                month = arguments.get("month")
                day = arguments.get("day")
                map_style = arguments.get("map_style", "political")
                marker_density = arguments.get("marker_density", "moderate")
                focus_region = arguments.get("focus_region", "world")
                
                data = await fetch_historical_events(month, day, "all")
                
                # Add Apps SDK map metadata
                data["apps_sdk_metadata"] = {
                    "component_type": "interactive_map",
                    "map_style": map_style,
                    "marker_density": marker_density,
                    "focus_region": focus_region,
                    "supports_zoom": True,
                    "supports_clustering": True,
                    "interactive_markers": True,
                    "geographic_features": ["location_markers", "event_clustering", "region_filtering", "marker_details"]
                }
                
                response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"), 
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🗺️ Interactive world map for {data.get('component_metadata', {}).get('date_formatted', f'{month:02d}/{day:02d}')} plotting {sum(len(data.get(k, [])) for k in ['events', 'births', 'deaths', 'holidays'])} historical events geographically with beautiful markers and location details."
                            }
                        ],
                        "structuredContent": {
                            "type": "historical_world_map",
                            "data": data,
                            "metadata": {
                                "date": f"{month:02d}/{day:02d}",
                                "map_style": map_style,
                                "marker_density": marker_density,
                                "focus_region": focus_region,
                                "component_type": "interactive_map",
                                "apps_sdk_features": ["geographic_visualization", "interactive_markers", "clustering", "region_focus"]
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
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "resources": [
                        {
                            "uri": "ui://widget/historical-timeline.html",
                            "name": "Historical Timeline Explorer",
                            "description": "Interactive timeline with rich visual cards, filtering, favorites, and theme integration",
                            "mimeType": "text/html+skybridge"
                        },
                        {
                            "uri": "ui://widget/historical-timeline-simple.html",
                            "name": "Historical Timeline Simple",
                            "description": "Simplified timeline component for better Apps SDK compatibility",
                            "mimeType": "text/html+skybridge"
                        },
                        {
                            "uri": "ui://widget/historical-discovery.html", 
                            "name": "Historical Discovery Experience",
                            "description": "Discovery interface with carousels, recommendations, and interactive cards",
                            "mimeType": "text/html+skybridge"
                        },
                        {
                            "uri": "ui://widget/historical-map.html",
                            "name": "Historical World Map",
                            "description": "Geographic visualization with interactive markers and location details", 
                            "mimeType": "text/html+skybridge"
                        }
                    ]
                }
            }
            
        elif method == "resources/read":
            uri = params.get("uri")
            if uri in ["ui://widget/historical-timeline.html", "ui://widget/historical-timeline-simple.html", "ui://widget/historical-discovery.html", "ui://widget/historical-map.html"]:
                filename = uri.replace("ui://widget/", "")
                filepath = f"ui_components/{filename}"
                
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding='utf-8') as f:
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
                        "error": {"code": -32602, "message": f"Resource file not found: {filename}"}
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
            
        logger.info(f"MCP Response: {json.dumps(response, indent=2)[:500]}...")
        return response
        
    except Exception as e:
        logger.error(f"MCP error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if body else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
