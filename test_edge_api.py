#!/usr/bin/env python3
"""
Test script to verify edge creation API for Swargate to Wakad
"""

import requests
import json

API_BASE = 'http://127.0.0.1:5000'

def test_edge_creation():
    """Test creating an edge between Swargate and Wakad"""
    
    print("Testing edge creation API...")
    print("=" * 50)
    
    # First add the locations
    locations = ["Swargate", "Wakad"]
    
    for loc in locations:
        try:
            response = requests.post(f"{API_BASE}/api/locations", 
                                   json={"name": loc})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Added {loc}: {data['coordinates']}")
            else:
                print(f"⚠️  {loc} might already exist")
        except Exception as e:
            print(f"Error adding {loc}: {e}")
    
    print()
    
    # Now create an edge between them
    try:
        response = requests.post(f"{API_BASE}/api/edges", json={
            "from": "Swargate",
            "to": "Wakad",
            "metric": "distance"
        })
        
        if response.status_code == 200:
            data = response.json()
            edge = data['edge']
            print(f"✅ Edge created:")
            print(f"   From: {edge['from']}")
            print(f"   To: {edge['to']}")
            print(f"   Distance: {edge['weight']:.2f} {edge['metric']}")
            print(f"   Bidirectional: {edge['bidirectional']}")
            
            if abs(edge['weight'] - 18.0) < 2.0:
                print("✅ Distance is accurate!")
            else:
                print("❌ Distance may need adjustment")
        else:
            print(f"❌ Error creating edge: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_edge_creation()
