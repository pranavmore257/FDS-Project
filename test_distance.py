#!/usr/bin/env python3
"""
Test script to verify distance calculation for Swargate to Wakad
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'FDSproject', 'backend'))

from app import get_driving_distance, get_coordinates

def test_swargate_wakad_distance():
    """Test the distance between Swargate and Wakad"""
    
    print("Testing Swargate to Wakad distance calculation...")
    print("=" * 50)
    
    # Get coordinates for both locations
    try:
        swargate_coords = get_coordinates("Swargate")
        wakad_coords = get_coordinates("Wakad")
        
        print(f"Swargate coordinates: {swargate_coords}")
        print(f"Wakad coordinates: {wakad_coords}")
        print()
        
        # Calculate distance using the updated function
        distance = get_driving_distance(swargate_coords, wakad_coords)
        
        print(f"Calculated distance: {distance:.2f} km")
        print(f"Expected distance: ~18 km")
        print()
        
        if abs(distance - 18.0) < 2.0:  # Allow 2km tolerance
            print("✅ Distance calculation looks accurate!")
        else:
            print("❌ Distance calculation may need adjustment")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_swargate_wakad_distance()
