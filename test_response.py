#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للتأكد من أن الاستجابات تعمل بشكل صحيح
"""

import asyncio
import requests
import json

def test_api_endpoint():
    """اختبار endpoint مباشرة"""
    url = "http://localhost:8001/get_player_name"
    
    # اختبار Free Fire
    test_data = {
        "player_id": "11442289597",
        "game_type": "freefire"
    }
    
    print("🧪 Testing Free Fire API...")
    print(f"Request: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # اختبار Jawaker
    test_data = {
        "player_id": "1230574182",
        "game_type": "jawaker"
    }
    
    print("🧪 Testing Jawaker API...")
    print(f"Request: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

async def test_direct_functions():
    """اختبار الدوال مباشرة"""
    try:
        from main import get_player_name_async
        
        print("🧪 Testing Free Fire Direct Function...")
        result = await get_player_name_async("11442289597", "freefire")
        print(f"Direct Result: {result}")
        
        print("\n🧪 Testing Jawaker Direct Function...")
        result = await get_player_name_async("1230574182", "jawaker")
        print(f"Direct Result: {result}")
        
    except Exception as e:
        print(f"Error in direct test: {e}")

if __name__ == "__main__":
    print("🚀 Testing API Responses")
    print("="*50)
    
    # اختبار API endpoint
    test_api_endpoint()
    
    print("\n" + "="*50 + "\n")
    
    # اختبار الدوال مباشرة
    asyncio.run(test_direct_functions())
