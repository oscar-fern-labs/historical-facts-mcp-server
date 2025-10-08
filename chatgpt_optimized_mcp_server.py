#!/usr/bin/env python3
"""
ChatGPT-Optimized Historical Facts MCP Server
Specifically designed to eliminate 424 errors in ChatGPT
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional
import httpx
import random
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatgpt-optimized-mcp")

# Wikipedia API
WIKI_API_BASE = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"

class ChatGPTOptimizedServer:
    """MCP Server optimized specifically for ChatGPT compatibility"""
    
    def __init__(self):
        self.app = FastAPI(title="Historical Facts MCP - ChatGPT Optimized")
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Set up CORS and middleware for ChatGPT compatibility"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        @self.app.middleware("http")
        async def chatgpt_optimization_middleware(request: Request, call_next):
            """Middleware to optimize for ChatGPT"""
            response = await call_next(request)
            
            # Add ChatGPT-friendly headers
            response.headers["Cache-Control"] = "no-cache"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Optimized-For"] = "ChatGPT"
            
            return response
    
    def setup_routes(self):
        """Set up MCP protocol routes"""
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """Handle MCP JSON-RPC requests"""
            try:
                body = await request.json()
                method = body.get("method")
                params = body.get("params", {})
                request_id = body.get("id", 1)
                
                logger.info(f"MCP Request: {method} with params: {params}")
                
                if method == "initialize":
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {
                                "name": "historical-facts-chatgpt-optimized",
                                "version": "3.0.0",
                                "description": "ChatGPT-optimized Historical Facts MCP Server - Zero 424 Errors"
                            }
                        }
                    })
                
                elif method == "notifications/initialized":
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {}
                    })
                
                elif method == "tools/list":
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "get_historical_facts",
                                    "description": "Get historical facts for a specific date with simplified, reliable output",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "date": {
                                                "type": "string",
                                                "description": "Date in YYYY-MM-DD format"
                                            },
                                            "category": {
                                                "type": "string",
                                                "enum": ["events", "births", "deaths", "all"],
                                                "description": "Category of historical facts"
                                            }
                                        },
                                        "required": ["date"]
                                    }
                                },
                                {
                                    "name": "get_todays_facts",
                                    "description": "Get historical facts for today's date",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "category": {
                                                "type": "string",
                                                "enum": ["events", "births", "deaths", "all"],
                                                "description": "Category of historical facts"
                                            }
                                        }
                                    }
                                },
                                {
                                    "name": "get_random_fact",
                                    "description": "Get a random historical fact",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "category": {
                                                "type": "string",
                                                "enum": ["events", "births", "deaths"],
                                                "description": "Category of historical facts"
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    })
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    
                    logger.info(f"Tool call: {tool_name} with args: {tool_args}")
                    
                    if tool_name == "get_historical_facts":
                        result = await self.get_historical_facts_optimized(tool_args)
                    elif tool_name == "get_todays_facts":
                        result = await self.get_todays_facts_optimized(tool_args)
                    elif tool_name == "get_random_fact":
                        result = await self.get_random_fact_optimized(tool_args)
                    else:
                        result = {
                            "error": f"Unknown tool: {tool_name}"
                        }
                    
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result.get("text", "No data available")
                                }
                            ] + (result.get("ui", []))
                        }
                    })
                
                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    })
                    
            except Exception as e:
                logger.error(f"MCP Handler error: {e}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }, status_code=200)  # Always return 200 for MCP
    
    async def fetch_wikipedia_safe(self, endpoint: str) -> dict:
        """Ultra-safe Wikipedia fetch with aggressive timeouts for ChatGPT"""
        try:
            # Very conservative settings for ChatGPT compatibility
            timeout = httpx.Timeout(8.0, connect=3.0)  # Much shorter timeouts
            limits = httpx.Limits(max_keepalive_connections=2, max_connections=3)
            
            async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"Wikipedia fetch failed: {e}")
            return {}
    
    async def get_historical_facts_optimized(self, args: dict) -> dict:
        """Get historical facts with ChatGPT optimization"""
        try:
            date_str = args.get("date", "")
            category = args.get("category", "events")
            
            if not date_str:
                return {"text": "Please provide a date in YYYY-MM-DD format"}
            
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                month, day = parsed_date.month, parsed_date.day
            except ValueError:
                return {"text": "Invalid date format. Please use YYYY-MM-DD"}
            
            # Fetch data with timeout protection
            endpoint = f"{WIKI_API_BASE}/{category}/{month:02d}/{day:02d}"
            
            # Use asyncio.wait_for for additional timeout protection
            try:
                data = await asyncio.wait_for(
                    self.fetch_wikipedia_safe(endpoint), 
                    timeout=10.0  # Hard timeout for ChatGPT
                )
            except asyncio.TimeoutError:
                logger.warning("Wikipedia request timed out")
                data = {}
            
            items = data.get(category, [])[:5]  # Limit to 5 items for ChatGPT
            
            if not items:
                return {
                    "text": f"No {category} found for {date_str}. Try a different date or category."
                }
            
            # Create simple text response for ChatGPT
            text_response = f"Historical {category} for {date_str}:\\n\\n"
            for i, item in enumerate(items, 1):
                title = item.get("text", "Historical Event")[:100]  # Truncate for ChatGPT
                description = item.get("extract", "")[:200]  # Limit description
                text_response += f"{i}. {title}\\n"
                if description:
                    text_response += f"   {description}\\n"
                text_response += "\\n"
            
            return {
                "text": text_response,
                "ui": []  # Simplified - no complex UI for reliability
            }
            
        except Exception as e:
            logger.error(f"get_historical_facts_optimized error: {e}")
            return {"text": f"Error retrieving historical facts: {str(e)}"}
    
    async def get_todays_facts_optimized(self, args: dict) -> dict:
        """Get today's historical facts optimized for ChatGPT"""
        today = datetime.now()
        return await self.get_historical_facts_optimized({
            "date": today.strftime("%Y-%m-%d"),
            "category": args.get("category", "events")
        })
    
    async def get_random_fact_optimized(self, args: dict) -> dict:
        """Get random historical fact optimized for ChatGPT"""
        # Generate random date
        import random
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe day range
        year = 2024  # Use current year for consistency
        
        random_date = f"{year}-{month:02d}-{day:02d}"
        return await self.get_historical_facts_optimized({
            "date": random_date,
            "category": args.get("category", "events")
        })

# Create server instance
server = ChatGPTOptimizedServer()
app = server.app

if __name__ == "__main__":
    print("🚀 Starting ChatGPT-Optimized Historical Facts MCP Server")
    print("📡 Optimized to eliminate 424 TaskGroup errors in ChatGPT")
    print("🎯 Ultra-conservative timeouts and error handling")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8009,  # New port for optimized version
        log_level="info"
    )
