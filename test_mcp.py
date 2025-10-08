#!/usr/bin/env python3
"""
MCP Server Test Script
Tests both MCP endpoints to verify functionality
"""
import requests
import json

def test_mcp_endpoint(url, name):
    """Test an MCP endpoint"""
    print(f"\n🧪 Testing {name}: {url}")
    
    try:
        # Test initialize
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
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Initialize: SUCCESS")
            print(f"   Server: {result['result']['serverInfo']['name']}")
            print(f"   Version: {result['result']['serverInfo']['version']}")
            
            # Test tools/list
            tools_payload = {
                "jsonrpc": "2.0",
                "id": 2, 
                "method": "tools/list",
                "params": {}
            }
            
            tools_response = requests.post(url, json=tools_payload, headers={"Content-Type": "application/json"})
            if tools_response.status_code == 200:
                tools_result = tools_response.json()
                tool_count = len(tools_result['result']['tools'])
                print(f"✅ Tools List: SUCCESS ({tool_count} tools)")
                for tool in tools_result['result']['tools']:
                    print(f"   - {tool['name']}: {tool['description'][:50]}...")
            else:
                print(f"❌ Tools List: FAILED ({tools_response.status_code})")
                
        else:
            print(f"❌ Initialize: FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection: FAILED - {e}")

def main():
    print("🔧 MCP Server Connectivity Test")
    print("=" * 50)
    
    # Test both MCP servers
    test_mcp_endpoint(
        "https://enhanced-apps-sdk-morphvm-87kmb6bw.http.cloud.morph.so/mcp",
        "Enhanced Apps SDK Server"
    )
    
    test_mcp_endpoint(
        "https://mcp-server-updated-morphvm-87kmb6bw.http.cloud.morph.so/mcp", 
        "Original MCP Server"
    )
    
    print("\n🏁 Test Complete!")
    print("\nℹ️  For ChatGPT Desktop, use the URLs with `/mcp` endpoint!")

if __name__ == "__main__":
    main()
