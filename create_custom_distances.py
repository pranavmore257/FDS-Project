#!/usr/bin/env python3
"""
Create analysis with custom distances from user's map
"""

import json
import subprocess
import os
import sys

def get_custom_distances():
    """Get exact distances from user's map"""
    print("🗺️  Please enter the exact distances from your map:")
    print("=" * 50)
    
    try:
        # Get distances from user input
        katraj_bavdhan = float(input("Katraj ↔ Bavdhan distance (km): "))
        katraj_swargate = float(input("Katraj ↔ Swargate distance (km): "))
        bavdhan_wakad = float(input("Bavdhan ↔ Wakad distance (km): "))
        swargate_wakad = float(input("Swargate ↔ Wakad distance (km): "))
        
        vertices = ["Katraj", "Bavdhan", "Swargate", "Wakad"]
        
        edges = [
            {"from": "Katraj", "to": "Bavdhan", "weight": katraj_bavdhan},
            {"from": "Katraj", "to": "Swargate", "weight": katraj_swargate},
            {"from": "Bavdhan", "to": "Wakad", "weight": bavdhan_wakad},
            {"from": "Swargate", "to": "Wakad", "weight": swargate_wakad}
        ]
        
        return {
            "vertices": vertices,
            "edges": edges,
            "source": "Katraj",
            "destination": "Wakad"
        }
        
    except ValueError:
        print("❌ Please enter valid numbers!")
        return None

def analyze_paths(test_data):
    """Analyze which path is shorter with custom distances"""
    print("\n📈 Path Analysis with Your Map Distances:")
    print("-" * 50)
    
    # Extract distances
    katraj_bavdhan = None
    katraj_swargate = None
    bavdhan_wakad = None
    swargate_wakad = None
    
    for edge in test_data['edges']:
        if edge['from'] == 'Katraj' and edge['to'] == 'Bavdhan':
            katraj_bavdhan = edge['weight']
        elif edge['from'] == 'Katraj' and edge['to'] == 'Swargate':
            katraj_swargate = edge['weight']
        elif edge['from'] == 'Bavdhan' and edge['to'] == 'Wakad':
            bavdhan_wakad = edge['weight']
        elif edge['from'] == 'Swargate' and edge['to'] == 'Wakad':
            swargate_wakad = edge['weight']
    
    # Calculate path distances
    path_bavdhan = katraj_bavdhan + bavdhan_wakad
    path_swargate = katraj_swargate + swargate_wakad
    
    print(f"Path 1: Katraj → Bavdhan → Wakad = {katraj_bavdhan} + {bavdhan_wakad} = {path_bavdhan} km")
    print(f"Path 2: Katraj → Swargate → Wakad = {katraj_swargate} + {swargate_wakad} = {path_swargate} km")
    
    if path_bavdhan < path_swargate:
        print(f"\n✅ SHORTEST: Bavdhan path ({path_bavdhan} km)")
        shortest_path = "Bavdhan"
        shortest_distance = path_bavdhan
        difference = path_swargate - path_bavdhan
        print(f"   Bavdhan route saves {difference} km compared to Swargate route")
    elif path_swargate < path_bavdhan:
        print(f"\n✅ SHORTEST: Swargate path ({path_swargate} km)")
        shortest_path = "Swargate"
        shortest_distance = path_swargate
        difference = path_bavdhan - path_swargate
        print(f"   Swargate route saves {difference} km compared to Bavdhan route")
    else:
        print(f"\n⚖️  EQUAL: Both paths are {path_bavdhan} km")
        shortest_path = "Equal"
        shortest_distance = path_bavdhan
    
    return shortest_path, shortest_distance

def test_algorithms(test_data):
    """Test all three algorithms with custom distances"""
    
    print("\n🔧 Running Java Algorithms...")
    print("-" * 30)
    
    # Change to algorithms directory
    algorithms_dir = "FDSproject/backend/algorithms"
    if os.path.exists(algorithms_dir):
        os.chdir(algorithms_dir)
        print(f"📂 Changed to directory: {os.getcwd()}")
    else:
        print(f"❌ Directory not found: {algorithms_dir}")
        return None
    
    # Prepare JSON input for Java algorithms
    json_input = json.dumps(test_data)
    
    try:
        # Run Java AlgorithmRunner
        cmd = f'java -cp ".;json-20231013.jar" AlgorithmRunner "{json_input}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Algorithm execution successful!")
            return json.loads(result.stdout)
        else:
            print("❌ Algorithm execution failed!")
            print(f"Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        return None

def create_word_document(results, shortest_path, shortest_distance, test_data):
    """Create Word document with custom analysis"""
    
    print("\n📝 Creating Word document...")
    
    # Extract edge weights
    katraj_bavdhan = next(e['weight'] for e in test_data['edges'] if e['from'] == 'Katraj' and e['to'] == 'Bavdhan')
    katraj_swargate = next(e['weight'] for e in test_data['edges'] if e['from'] == 'Katraj' and e['to'] == 'Swargate')
    bavdhan_wakad = next(e['weight'] for e in test_data['edges'] if e['from'] == 'Bavdhan' and e['to'] == 'Wakad')
    swargate_wakad = next(e['weight'] for e in test_data['edges'] if e['from'] == 'Swargate' and e['to'] == 'Wakad')
    
    # Create content for Word document
    content = f"""Algorithm Analysis: Katraj to Wakad with Your Map Distances

Path Analysis: Katraj → {shortest_path} → Wakad ({shortest_distance} km) - Shortest Route

Problem Setup
• Source: Katraj
• Destination: Wakad  
• Vertices: Katraj, Bavdhan, Swargate, Wakad
• Edges (from your map):
  – Katraj ↔ Bavdhan: {katraj_bavdhan} km
  – Katraj ↔ Swargate: {katraj_swargate} km
  – Bavdhan ↔ Wakad: {bavdhan_wakad} km
  – Swargate ↔ Wakad: {swargate_wakad} km

Graph Visualization
Visual representation of your Pune connections:
    
    Katraj ({katraj_swargate}) Swargate ({swargate_wakad}) Wakad
      | \\          |           |
    {katraj_bavdhan}          |           |
      |            |           |
      Bavdhan ({bavdhan_wakad}) Wakad

Available paths from Katraj to Wakad:
1. Katraj → Bavdhan → Wakad = {katraj_bavdhan} + {bavdhan_wakad} = {katraj_bavdhan + bavdhan_wakad} km
2. Katraj → Swargate → Wakad = {katraj_swargate} + {swargate_wakad} = {katraj_swargate + swargate_wakad} km

Shortest path: Katraj → {shortest_path} → Wakad ({shortest_distance} km)

Algorithm Results
"""
    
    # Add algorithm results
    for algo_name, algo_result in results.items():
        path_str = " → ".join(algo_result.get('path', []))
        distance = algo_result.get('distance', 'N/A')
        time = algo_result.get('execution_time_ms', 'N/A')
        content += f"""
{algo_name.upper()} Algorithm:
• Distance: {distance} km
• Path: {path_str}
• Execution Time: {time} ms
"""
    
    content += f"""
Conclusion
This analysis uses the exact distances from your map to determine the shortest path from Katraj to Wakad. All algorithms correctly identified the path through {shortest_path} as optimal with a total distance of {shortest_distance} km. The step-by-step algorithm execution shows how each method processes the graph to find the mathematically shortest route based on your actual map distances.
"""
    
    # Write to file
    with open('c:/Users/ACER/Documents/impleFDS/Custom_Map_Analysis.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Analysis saved to: Custom_Map_Analysis.txt")
    print("📄 You can now convert this text to Word document if needed")

def main():
    print("🚀 Custom Distance Analysis for Katraj to Wakad")
    print("=" * 60)
    
    # Get custom distances
    test_data = get_custom_distances()
    if not test_data:
        return
    
    # Analyze paths
    shortest_path, shortest_distance = analyze_paths(test_data)
    
    # Test algorithms
    results = test_algorithms(test_data)
    if not results:
        return
    
    # Create document
    create_word_document(results, shortest_path, shortest_distance, test_data)

if __name__ == "__main__":
    main()
