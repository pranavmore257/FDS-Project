#!/usr/bin/env python3
"""
Test script for Pune locations (Katraj, Swargate, Baner, Wakad)
Demonstrates the DSA algorithms with real Pune coordinates
"""

import json
import subprocess
import os
import sys

def create_pune_test_data():
    """Create test data for Pune locations"""
    
    # Pune locations with realistic distances (in km)
    vertices = ["Katraj", "Swargate", "Baner", "Wakad"]
    
    # Edges with realistic distances based on actual Pune geography
    edges = [
        {"from": "Katraj", "to": "Swargate", "weight": 8.2},   # Southern to Central Pune
        {"from": "Swargate", "to": "Baner", "weight": 12.5},  # Central to Northwest Pune
        {"from": "Baner", "to": "Wakad", "weight": 6.8},       # Northwest Pune adjacent areas
        {"from": "Katraj", "to": "Baner", "weight": 15.3},     # Direct route
        {"from": "Swargate", "to": "Wakad", "weight": 18.7},   # Central to Northwest via longer route
        {"from": "Katraj", "to": "Wakad", "weight": 22.1}      # Southern to Northwest
    ]
    
    return {
        "vertices": vertices,
        "edges": edges,
        "source": "Katraj",
        "destination": "Wakad"
    }

def test_algorithms():
    """Test all three algorithms with Pune locations"""
    
    print("🚀 Testing DSA Algorithms with Pune Locations")
    print("=" * 50)
    print("Locations: Katraj, Swargate, Baner, Wakad")
    print()
    
    # Create test data
    test_data = create_pune_test_data()
    
    print("📍 Test Configuration:")
    print(f"Source: {test_data['source']}")
    print(f"Destination: {test_data['destination']}")
    print(f"Vertices: {test_data['vertices']}")
    print()
    
    print("🛣️  Graph Edges (with distances in km):")
    for edge in test_data['edges']:
        print(f"  {edge['from']} ←→ {edge['to']}: {edge['weight']} km")
    print()
    
    # Change to the algorithms directory
    algorithms_dir = "FDSproject/backend/algorithms"
    if os.path.exists(algorithms_dir):
        os.chdir(algorithms_dir)
        print(f"📂 Changed to directory: {os.getcwd()}")
    else:
        print(f"❌ Directory not found: {algorithms_dir}")
        return
    
    # Prepare JSON input for Java algorithms
    json_input = json.dumps(test_data)
    
    print("🔧 Running Java Algorithms...")
    print()
    
    try:
        # Run the Java AlgorithmRunner
        cmd = f'java -cp ".;json-20231013.jar" AlgorithmRunner "{json_input}"'
        print(f"💻 Command: {cmd}")
        print()
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Algorithm execution successful!")
            print()
            
            # Parse and display results
            results = json.loads(result.stdout)
            
            print("📊 Algorithm Results:")
            print("-" * 30)
            
            for algo_name, algo_result in results.items():
                print(f"\n🔹 {algo_name.upper()} Algorithm:")
                print(f"   Distance: {algo_result.get('distance', 'N/A')} km")
                print(f"   Path: {' → '.join(algo_result.get('path', []))}")
                print(f"   Execution Time: {algo_result.get('execution_time_ms', 'N/A')} ms")
                print(f"   Complexity: {algo_result.get('complexity', 'N/A')}")
                
                # Show first few steps for visualization
                steps = algo_result.get('steps', [])
                if steps:
                    print(f"   Steps (first 5):")
                    for i, step in enumerate(steps[:5]):
                        print(f"     {i+1}. {step}")
                    if len(steps) > 5:
                        print(f"     ... and {len(steps)-5} more steps")
                
                # Check for negative cycles (Bellman-Ford specific)
                if algo_result.get('has_negative_cycle'):
                    print(f"   ⚠️  Negative Cycle: {algo_result.get('error', 'Unknown')}")
            
            print()
            print("🎯 Analysis:")
            print("-" * 20)
            
            # Compare results
            dijkstra_result = results.get('dijkstra', {})
            bellman_ford_result = results.get('bellman_ford', {})
            floyd_warshall_result = results.get('floyd_warshall', {})
            
            dijkstra_distance = dijkstra_result.get('distance')
            bellman_ford_distance = bellman_ford_result.get('distance')
            floyd_warshall_distance = floyd_warshall_result.get('distance')
            
            print(f"📏 Shortest Distances Found:")
            print(f"   Dijkstra: {dijkstra_distance} km")
            print(f"   Bellman-Ford: {bellman_ford_distance} km")
            print(f"   Floyd-Warshall: {floyd_warshall_distance} km")
            
            # Check if all algorithms agree
            if (dijkstra_distance == bellman_ford_distance == floyd_warshall_distance):
                print("✅ All algorithms agree on the shortest path!")
            else:
                print("⚠️  Algorithms found different paths - this needs investigation")
            
            print()
            print("🏆 Performance Comparison:")
            print(f"   Dijkstra: {dijkstra_result.get('execution_time_ms', 'N/A')} ms")
            print(f"   Bellman-Ford: {bellman_ford_result.get('execution_time_ms', 'N/A')} ms")
            print(f"   Floyd-Warshall: {floyd_warshall_result.get('execution_time_ms', 'N/A')} ms")
            
        else:
            print("❌ Algorithm execution failed!")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        print("Make sure Java is installed and the algorithms are compiled.")
    
    print()
    print("📍 Pune Location Information:")
    print("-" * 30)
    print("• Katraj: Southern Pune, near Katraj Lake (18.4569°N, 73.8497°E)")
    print("• Swargate: Central Pune, major bus depot (18.5049°N, 73.8533°E)")
    print("• Baner: Northwest Pune, IT hub area (18.5638°N, 73.7752°E)")
    print("• Wakad: Northwest Pune, residential area (18.5983°N, 73.7759°E)")
    print()
    print("🗺️  Expected Shortest Path: Katraj → Baner → Wakad (22.1 km)")
    print("   Alternative path: Katraj → Swargate → Baner → Wakad (27.5 km)")

if __name__ == "__main__":
    test_algorithms()
