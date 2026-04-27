#!/usr/bin/env python3
"""
Test script for specific Pune connections:
- Katraj ↔ Swargate
- Katraj ↔ Baner  
- Baner ↔ Wakad
- Swargate ↔ Wakad
"""

import json
import subprocess
import os
import sys

def create_specific_connections_test():
    """Create test data with specific connections as requested"""
    
    # Pune locations with specific connections only
    vertices = ["Katraj", "Swargate", "Baner", "Wakad"]
    
    # Only the specified connections
    edges = [
        {"from": "Katraj", "to": "Swargate", "weight": 8.2},   # Katraj ↔ Swargate
        {"from": "Katraj", "to": "Baner", "weight": 15.3},     # Katraj ↔ Baner
        {"from": "Baner", "to": "Wakad", "weight": 6.8},       # Baner ↔ Wakad
        {"from": "Swargate", "to": "Wakad", "weight": 18.7}    # Swargate ↔ Wakad
    ]
    
    return {
        "vertices": vertices,
        "edges": edges,
        "source": "Katraj",
        "destination": "Wakad"
    }

def test_algorithms():
    """Test all three algorithms with specific connections"""
    
    print("🚀 Testing DSA Algorithms with Specific Connections")
    print("=" * 60)
    print("Connections: Katraj↔Swargate, Katraj↔Baner, Baner↔Wakad, Swargate↔Wakad")
    print()
    
    # Create test data
    test_data = create_specific_connections_test()
    
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
                
                # Show all steps for visualization
                steps = algo_result.get('steps', [])
                if steps:
                    print(f"   Steps:")
                    for i, step in enumerate(steps):
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
            
            print()
            print("📈 Available Paths Analysis:")
            print("-" * 30)
            print("Possible paths from Katraj to Wakad:")
            print("1. Katraj → Swargate → Wakad = 8.2 + 18.7 = 26.9 km")
            print("2. Katraj → Baner → Wakad = 15.3 + 6.8 = 22.1 km")
            print("3. Katraj → Swargate → Baner → Wakad = 8.2 + 12.5 + 6.8 = 27.5 km")
            print("4. Katraj → Baner → Swargate → Wakad = 15.3 + 12.5 + 18.7 = 46.5 km")
            print()
            print("Shortest path should be: Katraj → Baner → Wakad (22.1 km)")
            
        else:
            print("❌ Algorithm execution failed!")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        print("Make sure Java is installed and the algorithms are compiled.")
    
    print()
    print("📍 Connection Information:")
    print("-" * 30)
    print("• Katraj ↔ Swargate: 8.2 km (Southern to Central Pune)")
    print("• Katraj ↔ Baner: 15.3 km (Southern to Northwest Pune)")
    print("• Baner ↔ Wakad: 6.8 km (Northwest Pune adjacent areas)")
    print("• Swargate ↔ Wakad: 18.7 km (Central to Northwest Pune)")
    print()
    print("🗺️  Expected Shortest Path: Katraj → Baner → Wakad (22.1 km)")
    print("   Alternative via Swargate: Katraj → Swargate → Wakad (26.9 km)")

if __name__ == "__main__":
    test_algorithms()
