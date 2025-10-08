#!/usr/bin/env python3
"""
Comprehensive Test Suite for Historical Facts MCP Server - Step 1 Verification

This script verifies that all components are working correctly:
1. MCP Protocol compliance
2. All three Apps SDK tools functioning
3. External accessibility
4. UI component serving
5. Error handling
6. Performance benchmarks
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Any
import sys

# Test Configuration
BASE_URL = "http://localhost:8005"
MCP_ENDPOINT = f"{BASE_URL}/mcp"
EXTERNAL_URL = "https://enhanced-apps-sdk-morphvm-87kmb6bw.http.cloud.morph.so/mcp"

class MCPTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        
        self.results.append(result)
        print(result)
    
    async def test_mcp_initialize(self):
        """Test MCP protocol initialization"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"}
                    }
                }
                
                response = await client.post(MCP_ENDPOINT, json=payload)
                data = response.json()
                
                # Check response structure
                valid = (
                    response.status_code == 200 and
                    "result" in data and
                    "serverInfo" in data["result"] and
                    data["result"]["serverInfo"]["name"] == "historical-facts-apps-sdk-enhanced"
                )
                
                self.log_test(
                    "MCP Initialize Protocol", 
                    valid,
                    f"Status: {response.status_code}, Server: {data.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("MCP Initialize Protocol", False, f"Error: {str(e)}")
            return False
    
    async def test_tools_list(self):
        """Test tools/list method"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                response = await client.post(MCP_ENDPOINT, json=payload)
                data = response.json()
                
                tools = data.get("result", {}).get("tools", [])
                expected_tools = [
                    "historical_timeline_explorer",
                    "historical_discovery_experience", 
                    "historical_world_map"
                ]
                
                found_tools = [tool["name"] for tool in tools]
                valid = all(tool in found_tools for tool in expected_tools)
                
                self.log_test(
                    "Tools List", 
                    valid,
                    f"Found {len(found_tools)} tools: {', '.join(found_tools)}"
                )
                
                return valid, tools
                
        except Exception as e:
            self.log_test("Tools List", False, f"Error: {str(e)}")
            return False, []
    
    async def test_timeline_explorer_tool(self):
        """Test historical_timeline_explorer tool"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "historical_timeline_explorer",
                        "arguments": {
                            "month": 10,
                            "day": 8,
                            "event_type": "events"
                        }
                    }
                }
                
                start_time = time.time()
                response = await client.post(MCP_ENDPOINT, json=payload)
                response_time = (time.time() - start_time) * 1000
                
                data = response.json()
                result = data.get("result", {})
                
                # Check response structure
                structured_content = result.get("structuredContent", {}).get("data", {})
                valid = (
                    response.status_code == 200 and
                    "structuredContent" in result and
                    len(structured_content.get("events", [])) > 0
                )
                
                event_count = len(structured_content.get("events", []))
                
                self.log_test(
                    "Timeline Explorer Tool", 
                    valid,
                    f"Retrieved {event_count} events in {response_time:.0f}ms"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("Timeline Explorer Tool", False, f"Error: {str(e)}")
            return False
    
    async def test_discovery_experience_tool(self):
        """Test historical_discovery_experience tool"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "historical_discovery_experience",
                        "arguments": {
                            "discovery_mode": "serendipity",
                            "focus_category": "events"
                        }
                    }
                }
                
                start_time = time.time()
                response = await client.post(MCP_ENDPOINT, json=payload)
                response_time = (time.time() - start_time) * 1000
                
                data = response.json()
                result = data.get("result", {})
                
                structured_content = result.get("structuredContent", {}).get("data", {})
                valid = (
                    response.status_code == 200 and
                    "structuredContent" in result and
                    len(structured_content.get("events", [])) > 0
                )
                
                rec_count = len(structured_content.get("recommendations", {}).get("related_dates", []))
                
                self.log_test(
                    "Discovery Experience Tool", 
                    valid,
                    f"Generated {rec_count} recommendations in {response_time:.0f}ms"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("Discovery Experience Tool", False, f"Error: {str(e)}")
            return False
    
    async def test_world_map_tool(self):
        """Test historical_world_map tool"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "historical_world_map",
                        "arguments": {
                            "month": 10,
                            "day": 8,
                            "map_style": "political",
                            "focus_region": "world"
                        }
                    }
                }
                
                start_time = time.time()
                response = await client.post(MCP_ENDPOINT, json=payload)
                response_time = (time.time() - start_time) * 1000
                
                data = response.json()
                result = data.get("result", {})
                
                structured_content = result.get("structuredContent", {}).get("data", {})
                valid = (
                    response.status_code == 200 and
                    "structuredContent" in result and
                    len(structured_content.get("events", [])) > 0
                )
                
                location_count = len(structured_content.get("geographic_data", {}).get("event_locations", []))
                
                self.log_test(
                    "World Map Tool", 
                    valid,
                    f"Mapped {location_count} locations in {response_time:.0f}ms"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("World Map Tool", False, f"Error: {str(e)}")
            return False
    
    async def test_ui_resources(self):
        """Test UI component resource serving"""
        resources_to_test = [
            "historical-timeline-simple.html",
            "historical-discovery.html", 
            "historical-map.html"
        ]
        
        all_valid = True
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for resource in resources_to_test:
                    response = await client.get(f"{BASE_URL}/resources/{resource}")
                    valid = response.status_code == 200 and "html" in response.text.lower()
                    
                    if not valid:
                        all_valid = False
                    
                    self.log_test(
                        f"UI Resource: {resource}",
                        valid,
                        f"Status: {response.status_code}, Size: {len(response.text)} chars"
                    )
                    
        except Exception as e:
            self.log_test("UI Resources", False, f"Error: {str(e)}")
            all_valid = False
            
        return all_valid
    
    async def test_external_accessibility(self):
        """Test external HTTPS accessibility"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "external-test", "version": "1.0.0"}
                    }
                }
                
                response = await client.post(EXTERNAL_URL, json=payload)
                data = response.json()
                
                valid = (
                    response.status_code == 200 and
                    "result" in data
                )
                
                self.log_test(
                    "External HTTPS Access",
                    valid,
                    f"External URL accessible via HTTPS"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("External HTTPS Access", False, f"Error: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test invalid method
                payload = {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "invalid/method"
                }
                
                response = await client.post(MCP_ENDPOINT, json=payload)
                data = response.json()
                
                valid = (
                    response.status_code == 200 and
                    "error" in data and
                    data["error"]["code"] == -32601  # Method not found
                )
                
                self.log_test(
                    "Error Handling",
                    valid,
                    f"Properly handles invalid methods with JSON-RPC error codes"
                )
                
                return valid
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive MCP Server Test Suite")
        print("=" * 60)
        
        # Core Protocol Tests
        await self.test_mcp_initialize()
        tools_valid, tools = await self.test_tools_list()
        
        # Tool Function Tests
        await self.test_timeline_explorer_tool()
        await self.test_discovery_experience_tool()
        await self.test_world_map_tool()
        
        # Infrastructure Tests
        await self.test_ui_resources()
        await self.test_external_accessibility()
        await self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for result in self.results:
            print(result)
        
        print(f"\n🎯 OVERALL SCORE: {self.passed_tests}/{self.total_tests} tests passed")
        print(f"📈 SUCCESS RATE: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("🏆 ALL TESTS PASSED - System is fully operational!")
            return True
        else:
            print("⚠️  Some tests failed - Review issues above")
            return False

async def main():
    """Main test execution"""
    tester = MCPTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ VERIFICATION COMPLETE: Step 1 requirements fully satisfied")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED: Issues found that need resolution")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
