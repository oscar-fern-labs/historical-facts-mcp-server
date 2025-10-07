#!/usr/bin/env python3
"""
Historical Facts MCP Server

A fun MCP server that provides historical facts from events that happened 
on the same date in history. Uses the Wikipedia "On This Day" API to fetch 
fascinating historical events, births, deaths, and other notable occurrences.

Author: romantic_franklin
License: MIT
"""

import asyncio
import logging
from datetime import datetime, date
from typing import Any, Sequence
import json
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Set up logging to stderr (not stdout - important for MCP!)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("historical-facts-mcp")

# Initialize the MCP server
server = Server("historical-facts-mcp")

# Wikipedia On This Day API base URL
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"


async def fetch_historical_events(month: int, day: int, event_type: str = "all") -> dict:
    """
    Fetch historical events from Wikipedia's On This Day API
    
    Args:
        month: Month (1-12)
        day: Day (1-31)
        event_type: Type of events to fetch ('all', 'events', 'births', 'deaths', 'holidays')
    
    Returns:
        Dictionary containing the API response
    """
    url = f"{WIKI_API_BASE}/{event_type}/{month:02d}/{day:02d}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching data from Wikipedia API: {e}")
        raise


def format_historical_event(event: dict) -> str:
    """Format a single historical event for display"""
    text = event.get('text', 'No description available')
    year = event.get('year', 'Unknown year')
    
    # Get additional context from pages if available
    pages = event.get('pages', [])
    if pages:
        main_page = pages[0]
        title = main_page.get('displaytitle', main_page.get('title', ''))
        extract = main_page.get('extract', '')
        
        if extract:
            # Limit extract length for readability
            extract = extract[:300] + "..." if len(extract) > 300 else extract
            return f"**{year}**: {text}\n\n*{title}*: {extract}"
    
    return f"**{year}**: {text}"


def format_birth_death_event(event: dict, event_type: str) -> str:
    """Format births or deaths events"""
    text = event.get('text', 'No description available')
    year = event.get('year', 'Unknown year')
    
    pages = event.get('pages', [])
    if pages:
        main_page = pages[0]
        title = main_page.get('displaytitle', main_page.get('title', ''))
        extract = main_page.get('extract', '')
        
        if extract:
            # Limit extract length for readability  
            extract = extract[:200] + "..." if len(extract) > 200 else extract
            icon = "🎂" if event_type == "births" else "⚰️"
            return f"{icon} **{year}**: {text}\n\n*About {title}*: {extract}"
    
    icon = "🎂" if event_type == "births" else "⚰️"
    return f"{icon} **{year}**: {text}"


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        Tool(
            name="get_historical_facts",
            description="Get historical facts for a specific date (month and day). Returns fascinating events, births, deaths, and holidays that occurred on this date throughout history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "month": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 12,
                        "description": "Month (1-12)"
                    },
                    "day": {
                        "type": "integer", 
                        "minimum": 1,
                        "maximum": 31,
                        "description": "Day (1-31)"
                    },
                    "event_type": {
                        "type": "string",
                        "enum": ["all", "events", "births", "deaths", "holidays"],
                        "default": "all",
                        "description": "Type of historical facts to retrieve"
                    }
                },
                "required": ["month", "day"],
            },
        ),
        Tool(
            name="get_todays_historical_facts", 
            description="Get historical facts for today's date (current date). Perfect for learning what happened on this day in history!",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "enum": ["all", "events", "births", "deaths", "holidays"],
                        "default": "all", 
                        "description": "Type of historical facts to retrieve"
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_random_historical_fact",
            description="Get a random historical fact from a random date in the year. Great for discovering surprising historical events!",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "enum": ["all", "events", "births", "deaths", "holidays"],
                        "default": "events",
                        "description": "Type of historical facts to retrieve"
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """
    Handle tool execution.
    Tools can modify server state and notify clients of changes.
    """
    if arguments is None:
        arguments = {}

    try:
        if name == "get_historical_facts":
            month = arguments.get("month")
            day = arguments.get("day")
            event_type = arguments.get("event_type", "all")
            
            if not month or not day:
                return [TextContent(
                    type="text",
                    text="Error: Both month and day are required parameters."
                )]
            
            # Validate date
            try:
                date(2024, month, day)  # Use 2024 as it's a leap year to handle Feb 29
            except ValueError:
                return [TextContent(
                    type="text", 
                    text=f"Error: Invalid date {month}/{day}. Please provide a valid month (1-12) and day."
                )]
            
            data = await fetch_historical_events(month, day, event_type)
            
            # Format the response
            response_parts = []
            response_parts.append(f"# Historical Facts for {month}/{day}")
            response_parts.append("")
            
            # Process different types of events
            if event_type == "all":
                # Events
                if "events" in data and data["events"]:
                    response_parts.append("## 📅 Historical Events")
                    for event in data["events"][:3]:  # Limit to 3 events
                        response_parts.append(format_historical_event(event))
                        response_parts.append("")
                
                # Births
                if "births" in data and data["births"]:
                    response_parts.append("## 🎂 Notable Births")
                    for birth in data["births"][:2]:  # Limit to 2 births
                        response_parts.append(format_birth_death_event(birth, "births"))
                        response_parts.append("")
                
                # Deaths
                if "deaths" in data and data["deaths"]:
                    response_parts.append("## ⚰️ Notable Deaths")
                    for death in data["deaths"][:2]:  # Limit to 2 deaths
                        response_parts.append(format_birth_death_event(death, "deaths"))
                        response_parts.append("")
                
                # Holidays
                if "holidays" in data and data["holidays"]:
                    response_parts.append("## 🎉 Holidays & Observances")
                    for holiday in data["holidays"][:2]:  # Limit to 2 holidays
                        response_parts.append(format_historical_event(holiday))
                        response_parts.append("")
            
            else:
                # Specific event type
                if event_type in data and data[event_type]:
                    event_title = {
                        "events": "📅 Historical Events", 
                        "births": "🎂 Notable Births",
                        "deaths": "⚰️ Notable Deaths",
                        "holidays": "🎉 Holidays & Observances"
                    }.get(event_type, "Historical Facts")
                    
                    response_parts.append(f"## {event_title}")
                    
                    for event in data[event_type][:5]:  # Show up to 5 events
                        if event_type in ["births", "deaths"]:
                            response_parts.append(format_birth_death_event(event, event_type))
                        else:
                            response_parts.append(format_historical_event(event))
                        response_parts.append("")
                else:
                    response_parts.append(f"No {event_type} found for {month}/{day}.")
            
            return [TextContent(type="text", text="\n".join(response_parts))]
        
        elif name == "get_todays_historical_facts":
            today = datetime.now()
            event_type = arguments.get("event_type", "all")
            
            data = await fetch_historical_events(today.month, today.day, event_type)
            
            # Format the response
            response_parts = []
            response_parts.append(f"# What Happened on This Day ({today.month}/{today.day})")
            response_parts.append("")
            
            # Process the same way as get_historical_facts
            if event_type == "all":
                # Events
                if "events" in data and data["events"]:
                    response_parts.append("## 📅 Historical Events")
                    for event in data["events"][:3]:  
                        response_parts.append(format_historical_event(event))
                        response_parts.append("")
                
                # Births
                if "births" in data and data["births"]:
                    response_parts.append("## 🎂 Notable Births")
                    for birth in data["births"][:2]:  
                        response_parts.append(format_birth_death_event(birth, "births"))
                        response_parts.append("")
                
                # Deaths  
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
            
            return [TextContent(type="text", text="\n".join(response_parts))]
        
        elif name == "get_random_historical_fact":
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
                response_parts.append(f"No {event_type} found for {month}/{day}. Try again!")
            
            return [TextContent(type="text", text="\n".join(response_parts))]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point for the server."""
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
