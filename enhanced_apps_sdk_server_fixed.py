#!/usr/bin/env python3
"""
Enhanced Historical Facts MCP Server with ChatGPT-Compatible UI Rendering
This version embeds data directly into HTML templates for proper ChatGPT rendering
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
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
import uvicorn

# Wikipedia On This Day API base URL
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historical-facts-apps-sdk-fixed")

# Global state for demo
user_favorites = []
user_preferences = {
    "preferred_categories": ["events", "births"],
    "discovery_mode": "chronological"
}

async def fetch_single_endpoint(client: httpx.AsyncClient, endpoint: str) -> tuple[str, dict]:
    """Fetch a single endpoint with proper error handling"""
    try:
        response = await client.get(endpoint)
        response.raise_for_status()
        data = response.json()
        category = endpoint.split('/')[-3]  # Extract category from URL
        return category, data.get(category, [])[:20]  # Limit to 20 items
    except Exception as e:
        logger.warning(f"Failed to fetch {endpoint}: {e}")
        category = endpoint.split('/')[-3]
        return category, []

async def fetch_historical_events(month: int, day: int, event_type: str = "all") -> dict:
    """Fetch historical events from Wikipedia API with improved error handling"""
    
    endpoints = []
    if event_type in ("all", "events"):
        endpoints.append(f"{WIKI_API_BASE}/events/{month:02d}/{day:02d}")
    if event_type in ("all", "births"):
        endpoints.append(f"{WIKI_API_BASE}/births/{month:02d}/{day:02d}")
    if event_type in ("all", "deaths"):
        endpoints.append(f"{WIKI_API_BASE}/deaths/{month:02d}/{day:02d}")
    if event_type in ("all", "holidays"):
        endpoints.append(f"{WIKI_API_BASE}/holidays/{month:02d}/{day:02d}")
    
    all_data = {"events": [], "births": [], "deaths": [], "holidays": []}
    
    try:
        # Use httpx.AsyncClient with proper timeout and limits
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            # Fetch all endpoints concurrently with asyncio.gather
            tasks = [fetch_single_endpoint(client, endpoint) for endpoint in endpoints]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Task failed: {result}")
                    continue
                    
                category, data = result
                all_data[category] = data
                
    except Exception as e:
        logger.error(f"Critical error in fetch_historical_events: {e}")
        # Return default data structure even if everything fails
        pass
    
    # Add metadata
    all_data["component_metadata"] = {
        "total_events": len(all_data["events"]),
        "total_births": len(all_data["births"]),
        "total_deaths": len(all_data["deaths"]),
        "total_holidays": len(all_data["holidays"]),
        "date_formatted": f"{date(2000, month, day).strftime('%B %d')}",
        "has_images": any(
            item.get("thumbnail") or item.get("originalimage") 
            for category in ["events", "births", "deaths", "holidays"]
            for item in all_data[category] if isinstance(item, dict)
        )
    }
    
    return all_data

def generate_timeline_html(data: dict, month: int, day: int, view_mode: str = "timeline") -> str:
    """Generate complete HTML with embedded data for timeline component"""
    
    date_formatted = data["component_metadata"]["date_formatted"]
    stats = data["component_metadata"]
    
    # Generate event cards HTML
    def create_event_card(item, category):
        year = item.get("year", "Unknown")
        text = item.get("text", "No description available")
        
        # Truncate text if too long
        if len(text) > 200:
            text = text[:197] + "..."
            
        # Get image if available
        image_html = ""
        if item.get("thumbnail"):
            image_html = f'<img src="{item["thumbnail"]}" alt="Historical image" class="event-image">'
        
        category_colors = {
            "events": "#667eea",
            "births": "#48bb78", 
            "deaths": "#ed8936",
            "holidays": "#9f7aea"
        }
        
        color = category_colors.get(category, "#667eea")
        
        return f'''
        <div class="event-card" data-category="{category}">
            <div class="event-year" style="background: {color}">{year}</div>
            {image_html}
            <div class="event-title">{text}</div>
            <div class="event-category">{category.title()}</div>
        </div>
        '''
    
    # Generate all event cards
    all_cards = []
    for category in ["events", "births", "deaths", "holidays"]:
        for item in data.get(category, []):
            all_cards.append(create_event_card(item, category))
    
    cards_html = "".join(all_cards)
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historical Timeline - {date_formatted}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #f9f9f9;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .timeline-container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
        }}
        
        .timeline-header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
        }}
        
        .timeline-date {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .timeline-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-number {{ 
            font-size: 2rem; 
            font-weight: bold; 
        }}
        
        .stat-label {{ 
            font-size: 0.9rem; 
            opacity: 0.9; 
            margin-top: 5px;
        }}
        
        .filter-tabs {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .filter-tab {{
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            background: #e0e0e0;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }}
        
        .filter-tab.active {{
            background: #667eea;
            color: white;
        }}
        
        .timeline-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .event-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
        }}
        
        .event-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .event-year {{
            color: white;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }}
        
        .event-title {{
            font-size: 1rem;
            line-height: 1.4;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .event-category {{
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 0.75rem;
            color: #666;
            background: #f0f0f0;
            padding: 3px 8px;
            border-radius: 10px;
        }}
        
        .event-image {{
            width: 100%;
            max-height: 150px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .timeline-date {{
                font-size: 2rem;
            }}
            .timeline-grid {{
                grid-template-columns: 1fr;
            }}
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="timeline-container">
        <div class="timeline-header">
            <div class="timeline-date">{date_formatted}</div>
            <div class="timeline-subtitle">🕰️ Historical Timeline Explorer</div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{stats["total_events"]}</div>
                    <div class="stat-label">Events</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats["total_births"]}</div>
                    <div class="stat-label">Births</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats["total_deaths"]}</div>
                    <div class="stat-label">Deaths</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats["total_holidays"]}</div>
                    <div class="stat-label">Holidays</div>
                </div>
            </div>
        </div>
        
        <div class="filter-tabs">
            <button class="filter-tab active" onclick="filterEvents('all')">All</button>
            <button class="filter-tab" onclick="filterEvents('events')">Events</button>
            <button class="filter-tab" onclick="filterEvents('births')">Births</button>
            <button class="filter-tab" onclick="filterEvents('deaths')">Deaths</button>
            <button class="filter-tab" onclick="filterEvents('holidays')">Holidays</button>
        </div>
        
        <div class="timeline-grid" id="eventsGrid">
            {cards_html}
        </div>
    </div>
    
    <script>
        function filterEvents(category) {{
            // Update active tab
            document.querySelectorAll('.filter-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Show/hide cards
            const cards = document.querySelectorAll('.event-card');
            cards.forEach(card => {{
                if (category === 'all' || card.dataset.category === category) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
    '''

def generate_discovery_html(data: dict) -> str:
    """Generate HTML for discovery experience"""
    
    # Pick random items from different categories
    featured_items = []
    for category in ["events", "births", "deaths", "holidays"]:
        items = data.get(category, [])
        if items:
            featured_items.extend(random.sample(items, min(3, len(items))))
    
    random.shuffle(featured_items)
    featured_items = featured_items[:12]  # Show 12 featured items
    
    cards_html = ""
    category_colors = {
        "events": "#667eea",
        "births": "#48bb78", 
        "deaths": "#ed8936",
        "holidays": "#9f7aea"
    }
    
    for i, item in enumerate(featured_items):
        # Determine category based on the data structure
        category = "events"  # Default
        for cat in ["events", "births", "deaths", "holidays"]:
            if item in data.get(cat, []):
                category = cat
                break
                
        year = item.get("year", "Unknown")
        text = item.get("text", "No description available")
        
        if len(text) > 150:
            text = text[:147] + "..."
            
        color = category_colors.get(category, "#667eea")
        
        cards_html += f'''
        <div class="discovery-card" style="animation-delay: {i * 0.1}s">
            <div class="discovery-year" style="background: {color}">{year}</div>
            <div class="discovery-text">{text}</div>
            <div class="discovery-category">{category.title()}</div>
        </div>
        '''
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historical Discovery Experience</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .discovery-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .discovery-header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .discovery-title {{
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .discovery-subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .discovery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }}
        
        .discovery-card {{
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            opacity: 0;
            animation: slideInUp 0.6s ease forwards;
        }}
        
        .discovery-card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .discovery-year {{
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }}
        
        .discovery-text {{
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 15px;
        }}
        
        .discovery-category {{
            font-size: 0.8rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        
        @keyframes slideInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 768px) {{
            .discovery-title {{
                font-size: 2rem;
            }}
            .discovery-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="discovery-container">
        <div class="discovery-header">
            <div class="discovery-title">🌟 Historical Discovery</div>
            <div class="discovery-subtitle">Explore fascinating moments from history</div>
        </div>
        
        <div class="discovery-grid">
            {cards_html}
        </div>
    </div>
</body>
</html>
    '''

def generate_world_map_html(data: dict, month: int, day: int) -> str:
    """Generate HTML for world map visualization"""
    
    date_formatted = data["component_metadata"]["date_formatted"]
    
    # Create a simple world map visualization with event markers
    events_with_locations = []
    
    # Sample location mapping for demo (in real app, would use geocoding)
    location_mapping = {
        "United States": {"lat": 39.8283, "lng": -98.5795, "country": "USA"},
        "France": {"lat": 46.6034, "lng": 1.8883, "country": "France"},
        "Germany": {"lat": 51.1657, "lng": 10.4515, "country": "Germany"},
        "United Kingdom": {"lat": 55.3781, "lng": -3.4360, "country": "UK"},
        "Russia": {"lat": 61.5240, "lng": 105.3188, "country": "Russia"},
        "China": {"lat": 35.8617, "lng": 104.1954, "country": "China"},
        "Japan": {"lat": 36.2048, "lng": 138.2529, "country": "Japan"},
        "Italy": {"lat": 41.8719, "lng": 12.5674, "country": "Italy"},
    }
    
    # Extract events with approximate locations
    for category in ["events", "births", "deaths"]:
        for item in data.get(category, [])[:10]:  # Limit for demo
            text = item.get("text", "")
            year = item.get("year", "Unknown")
            
            # Simple location detection
            location = None
            for country, coords in location_mapping.items():
                if country in text or coords["country"] in text:
                    location = coords
                    break
                    
            if location:
                events_with_locations.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "year": year,
                    "category": category,
                    "location": location
                })
    
    markers_html = ""
    for i, event in enumerate(events_with_locations[:15]):  # Limit to 15 markers
        lat, lng = event["location"]["lat"], event["location"]["lng"]
        # Convert lat/lng to approximate screen coordinates (simplified projection)
        x = int((lng + 180) * (800 / 360))
        y = int((90 - lat) * (400 / 180))
        
        color = {"events": "#667eea", "births": "#48bb78", "deaths": "#ed8936"}.get(event["category"], "#667eea")
        
        markers_html += f'''
        <div class="map-marker" style="left: {x}px; top: {y}px; background: {color}" 
             title="{event['year']}: {event['text']}" data-year="{event['year']}" 
             data-category="{event['category']}">
            <span class="marker-year">{event['year']}</span>
        </div>
        '''
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historical World Map - {date_formatted}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #1a202c;
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .map-container {{
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }}
        
        .map-header {{
            margin-bottom: 30px;
        }}
        
        .map-title {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .map-subtitle {{
            font-size: 1.1rem;
            opacity: 0.8;
        }}
        
        .world-map {{
            position: relative;
            width: 800px;
            height: 400px;
            margin: 0 auto;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400"><rect width="800" height="400" fill="%23234e52"/><path d="M150,100 L200,80 L250,90 L300,85 L350,95 L400,90 L450,85 L500,90 L550,85 L600,95 L650,90 L700,85" stroke="%23319795" stroke-width="2" fill="none"/><path d="M100,150 L150,140 L200,145 L250,140 L300,150 L350,145 L400,140 L450,145 L500,140 L550,150 L600,145 L650,140 L700,145" stroke="%234fd1c7" stroke-width="2" fill="none"/></svg>') center/cover;
            border-radius: 15px;
            border: 3px solid #4a5568;
            overflow: hidden;
        }}
        
        .map-marker {{
            position: absolute;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
            z-index: 10;
        }}
        
        .map-marker:hover {{
            transform: scale(2);
            z-index: 20;
        }}
        
        .marker-year {{
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .map-marker:hover .marker-year {{
            opacity: 1;
        }}
        
        .map-legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 currentColor; }}
            70% {{ box-shadow: 0 0 0 10px transparent; }}
            100% {{ box-shadow: 0 0 0 0 transparent; }}
        }}
        
        @media (max-width: 900px) {{
            .world-map {{
                width: 90vw;
                height: calc(90vw * 0.5);
                max-width: 800px;
                max-height: 400px;
            }}
            .map-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="map-container">
        <div class="map-header">
            <div class="map-title">🗺️ Historical World Map</div>
            <div class="map-subtitle">{date_formatted} - Events across the globe</div>
        </div>
        
        <div class="world-map">
            {markers_html}
        </div>
        
        <div class="map-legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #667eea;"></div>
                <span>Historical Events</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #48bb78;"></div>
                <span>Notable Births</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ed8936;"></div>
                <span>Notable Deaths</span>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Enhanced Apps SDK MCP Server starting up...")
    yield
    logger.info("👋 Enhanced Apps SDK MCP Server shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Historical Facts Apps SDK MCP Server - Fixed",
    description="Enhanced MCP server with ChatGPT-compatible UI rendering",
    version="2.1.0",
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

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "Historical Facts Apps SDK MCP Server - Fixed",
        "version": "2.1.0",
        "description": "Enhanced MCP server showcasing ALL OpenAI Apps SDK capabilities with proper ChatGPT rendering",
        "mcp_endpoint": "/mcp",
        "features": [
            "ChatGPT-compatible UI rendering",
            "Embedded data templates",
            "Interactive timeline explorer",
            "Discovery experience with recommendations", 
            "World map with geographic visualization",
            "Full MCP protocol compliance",
            "Rich visual components"
        ],
        "tools": [
            "historical_timeline_explorer",
            "historical_discovery_experience", 
            "historical_world_map"
        ]
    }

@app.post("/mcp")
async def mcp_handler(request: Request):
    """Handle MCP protocol requests with embedded UI rendering"""
    
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    
    logger.info(f"MCP Request: {method}")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "historical-facts-apps-sdk-fixed",
                    "version": "2.1.0",
                    "description": "Enhanced Historical Facts MCP Server with ChatGPT-compatible UI rendering"
                }
            }
        }
        
    elif method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": body.get("id"), "result": {}}
        
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", 
            "id": body.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "historical_timeline_explorer",
                        "description": "🕰️ Interactive historical timeline with rich visual cards, filtering, and favorites system. Now with ChatGPT-compatible rendering!",
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
                        }
                    },
                    {
                        "name": "historical_discovery_experience", 
                        "description": "🌟 Immersive historical discovery with smart recommendations and beautiful cards. Perfect for exploring history!",
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
                        }
                    },
                    {
                        "name": "historical_world_map",
                        "description": "🗺️ Interactive world map plotting historical events geographically with beautiful markers and location details.",
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
            html_content = generate_timeline_html(data, month, day, view_mode)
            
            total_items = sum(len(data.get(k, [])) for k in ['events', 'births', 'deaths', 'holidays'])
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"🕰️ Interactive historical timeline for {data['component_metadata']['date_formatted']} with {total_items} historical items. Features rich visual cards, smart filtering, and responsive design."
                        },
                        {
                            "type": "html",
                            "html": html_content
                        }
                    ]
                }
            }
            
        elif tool_name == "historical_discovery_experience":
            discovery_mode = arguments.get("discovery_mode", "serendipity")
            focus_category = arguments.get("focus_category", "all")
            time_period = arguments.get("time_period", "any")
            
            # Generate random date for discovery
            if discovery_mode == "serendipity":
                month, day = random.randint(1, 12), random.randint(1, 28)
            else:
                # Use today's date for other modes
                today = datetime.now()
                month, day = today.month, today.day
                
            data = await fetch_historical_events(month, day, focus_category)
            html_content = generate_discovery_html(data)
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"), 
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🌟 Historical discovery experience in {discovery_mode} mode, focusing on {focus_category} from the {time_period} period. Explore fascinating moments from history through beautiful interactive cards!"
                        },
                        {
                            "type": "html", 
                            "html": html_content
                        }
                    ]
                }
            }
            
        elif tool_name == "historical_world_map":
            month = arguments.get("month")
            day = arguments.get("day")
            map_style = arguments.get("map_style", "political")
            marker_density = arguments.get("marker_density", "moderate") 
            focus_region = arguments.get("focus_region", "world")
            
            data = await fetch_historical_events(month, day, "all")
            html_content = generate_world_map_html(data, month, day)
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🗺️ Interactive world map for {data['component_metadata']['date_formatted']} showing historical events across the globe. Features geographic visualization with interactive markers and location details."
                        },
                        {
                            "type": "html",
                            "html": html_content 
                        }
                    ]
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            
    elif method in ["resources/list", "prompts/list"]:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {method.split('/')[0]: []}
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced Apps SDK MCP Server with ChatGPT-compatible rendering...")
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8005,
        log_level="info"
    )
