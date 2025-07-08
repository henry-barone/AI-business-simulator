#!/usr/bin/env python3
"""
Quick test script to verify the API is working.
"""

import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:5001/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_company_creation():
    """Test company creation endpoint"""
    try:
        data = {
            "name": "Test Company",
            "industry": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/companies", 
                               json=data,
                               headers={"Content-Type": "application/json"})
        print(f"Company creation: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Company creation failed: {e}")
    return False

if __name__ == "__main__":
    print("Testing Backend API...")
    print("=" * 40)
    
    if test_health():
        print("✓ Health endpoint working")
        if test_company_creation():
            print("✓ Company creation working")
        else:
            print("✗ Company creation failed")
    else:
        print("✗ Backend not responding")
        print("Make sure to start the backend with: python app.py")