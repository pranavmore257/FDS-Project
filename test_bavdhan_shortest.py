#!/usr/bin/env python3
"""
Test script where Bavdhan path is shorter than Swargate path
"""

import json
import subprocess
import os
import sys

def create_bavdhan_shortest_test():
    """Create test data where Bavdhan path is shorter"""
    
    vertices = ["Katraj", "Bavdhan", "Swargate", "Wakad"]
    
    # Real Pune distances (let algorithm find true shortest path)
    edges = [
        {"from": "Katraj", "to": "Bavdhan", "weight": 16.8},   # Katraj ↔ Bavdhan (real)
        {"from": "Katraj", "to": "Swargate", "weight": 8.2},   # Katraj ↔ Swargate (real)
        {"from": "Bavdhan", "to": "Wakad", "weight": 13.7},    # Bavdhan ↔ Wakad (real)
        {"from": "Swargate", "to": "Wakad", "weight": 18.7}    # Swargate ↔ Wakad (real)
    ]
    
    return {
        "vertices": vertices,
        "edges": edges,
        "source": "Katraj",
        "destination": "Wakad"
    }

def test_algorithms():
    """Test all three algorithms with Bavdhan as shortest"""
    
    print("🚀 Testing DSA Algorithms - Bavdhan Path Shortest")
    print("=" * 60)
    print("Connections: Katraj↔Bavdhan, Katraj↔Swargate, Bavdhan↔Wakad, Swargate↔Wakad")
    print()
    
    # Create test data
    test_data = create_bavdhan_shortest_test()
    
    print("📍 Test Configuration:")
    print(f"Source: {test_data['source']}")
    print(f"Destination: {test_data['destination']}")
    print(f"Vertices: {test_data['vertices']}")
    print()
    
    print("🛣️  Graph Edges (with distances in km):")
    for edge in test_data['edges']:
        print(f"  {edge['from']} ←→ {edge['to']}: {edge['weight']} km")
    print()
    
    print("📈 Available Paths Analysis:")
    print("-" * 30)
    print("Possible paths from Katraj to Wakad:")
    print("1. Katraj → Bavdhan → Wakad = 16.8 + 13.7 = 30.5 km")
    print("2. Katraj → Swargate → Wakad = 8.2 + 18.7 = 26.9 km ✓ SHORTEST")
    print()
    print("Expected: Swargate path should be chosen (26.9 km) - real shortest path")
    print()
    
    # Change to algorithms directory
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
        # Run Java AlgorithmRunner
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
                
                # Check if path goes through Bavdhan
                path = algo_result.get('path', [])
                if 'Bavdhan' in path:
                    print(f"   ✅ Path goes through BAVDHAN as expected!")
                elif 'Swargate' in path:
                    print(f"   ⚠️  Path goes through Swargate, not Bavdhan")
                else:
                    print(f"   ❓ Path takes unexpected route")
            
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
                print("✅ All algorithms agree on shortest path!")
                if dijkstra_distance == 26.9:
                    print("🎯 CORRECT: All algorithms found Swargate path (real shortest)!")
                else:
                    print("⚠️  Algorithms found different path than expected")
            else:
                print("⚠️  Algorithms found different paths - this needs investigation")
            
        else:
            print("❌ Algorithm execution failed!")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        print("Make sure Java is installed and algorithms are compiled.")

if __name__ == "__main__":
    test_algorithms()
