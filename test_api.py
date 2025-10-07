#!/usr/bin/env python3
"""
Test script to verify Wikipedia API functionality
"""
import asyncio
import httpx
import json


async def test_wikipedia_api():
    """Test the Wikipedia On This Day API"""
    url = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/01/15"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            print("✅ Wikipedia API is working!")
            print(f"📅 Events found: {len(data.get('events', []))}")
            print(f"🎂 Births found: {len(data.get('births', []))}")
            print(f"⚰️ Deaths found: {len(data.get('deaths', []))}")
            print(f"🎉 Holidays found: {len(data.get('holidays', []))}")
            
            # Show a sample event
            if data.get('events'):
                sample_event = data['events'][0]
                print(f"\n📚 Sample event: {sample_event.get('text', 'No text')}")
                print(f"🗓️ Year: {sample_event.get('year', 'Unknown')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing Wikipedia API: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_wikipedia_api())
