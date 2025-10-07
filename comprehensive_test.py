#!/usr/bin/env python3
"""
Comprehensive test suite for Historical Facts MCP Server
Tests all endpoints, tools, and integration points
"""

import asyncio
import json
import sys
from datetime import datetime
import httpx


BASE_URL = "https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so"

async def test_health_endpoint():
    """Test the health check endpoint"""
    print("🩺 Testing health endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
        return True


async def test_root_endpoint():
    """Test the root information endpoint"""
    print("🏠 Testing root endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Historical Facts MCP Server"
        assert "endpoints" in data
        print("✅ Root endpoint passed")
        return True


async def test_specific_date_endpoint():
    """Test getting facts for a specific date"""
    print("📅 Testing specific date endpoint (July 4th)...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/7/4")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "07/04"
        assert "event_types" in data
        assert len(data["event_types"]) > 0
        print(f"✅ Found {len(data['event_types'])} event types for July 4th")
        return True


async def test_today_endpoint():
    """Test getting today's historical facts"""
    print("📆 Testing today's facts endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/today")
        assert response.status_code == 200
        data = response.json()
        today = datetime.now()
        expected_date = f"{today.month:02d}/{today.day:02d}"
        assert data["date"] == expected_date
        print(f"✅ Today's facts for {expected_date} retrieved successfully")
        return True


async def test_random_endpoint():
    """Test getting random historical facts"""
    print("🎲 Testing random facts endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/random")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "event_type" in data
        assert "fact" in data
        print(f"✅ Random fact for {data['date']} retrieved successfully")
        return True


async def test_event_type_filtering():
    """Test event type filtering"""
    print("🔍 Testing event type filtering...")
    event_types = ["events", "births", "deaths"]
    
    for event_type in event_types:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/historical-facts/1/1?event_type={event_type}")
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "01/01"
            if data["event_types"]:
                assert data["event_types"][0]["type"] == event_type
        print(f"  ✅ {event_type} filtering works")
    
    return True


async def test_mcp_tool_calls():
    """Test MCP-compatible tool calls"""
    print("🔧 Testing MCP tool calls...")
    
    # Test get_todays_historical_facts
    tool_request = {
        "name": "get_todays_historical_facts",
        "arguments": {"event_type": "events"}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/mcp/call-tool",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        print("  ✅ get_todays_historical_facts tool call works")
    
    # Test get_historical_facts
    tool_request = {
        "name": "get_historical_facts",
        "arguments": {"month": 12, "day": 25, "event_type": "all"}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/mcp/call-tool",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        print("  ✅ get_historical_facts tool call works")
    
    # Test get_random_historical_fact
    tool_request = {
        "name": "get_random_historical_fact",
        "arguments": {"event_type": "events"}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/mcp/call-tool",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        print("  ✅ get_random_historical_fact tool call works")
    
    return True


async def test_error_handling():
    """Test error handling"""
    print("⚠️  Testing error handling...")
    
    # Test invalid date
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/13/40")
        assert response.status_code == 400
        print("  ✅ Invalid date handling works")
    
    # Test invalid event type
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/1/1?event_type=invalid")
        assert response.status_code == 400
        print("  ✅ Invalid event type handling works")
    
    return True


async def test_data_quality():
    """Test data quality and format"""
    print("📊 Testing data quality...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/historical-facts/1/15")
        data = response.json()
        
        # Check structure
        assert "date" in data
        assert "event_types" in data
        
        # Check event structure if events exist
        if data["event_types"]:
            event_type = data["event_types"][0]
            assert "type" in event_type
            assert "count" in event_type
            assert "events" in event_type
            
            if event_type["events"]:
                event = event_type["events"][0]
                assert "year" in event
                assert "text" in event
                assert "pages" in event
        
        print("  ✅ Data structure is valid")
    
    return True


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive test suite for Historical Facts MCP Server")
    print("=" * 80)
    
    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_specific_date_endpoint,
        test_today_endpoint,
        test_random_endpoint,
        test_event_type_filtering,
        test_mcp_tool_calls,
        test_error_handling,
        test_data_quality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print("=" * 80)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The Historical Facts MCP Server is fully functional!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
