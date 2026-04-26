# Advanced Route Finder with Multiple Algorithms

A sophisticated route finding application that compares three shortest-path algorithms: **Dijkstra**, **Bellman-Ford**, and **Floyd-Warshall**. The application features real-time map visualization, algorithm performance comparison, and persistent location storage.

## Features

✨ **Three Shortest Path Algorithms**
- ⚡ **Dijkstra**: Fast greedy algorithm using priority queue (O((V + E) log V))
- 🔄 **Bellman-Ford**: Handles negative weights, detects negative cycles (O(V × E))
- 📊 **Floyd-Warshall**: Computes all-pairs shortest paths (O(V³))

🎯 **Performance Comparison**
- Execute all three algorithms simultaneously
- Compare execution times in milliseconds
- Analyze time complexity for each algorithm
- Visual performance summary with fastest/slowest indicators

📍 **Location Management**
- Hashtable-based persistent storage of locations
- Geocoding with Google Maps and OpenStreetMap (Nominatim)
- Support for fallback location approximation
- Retrieve any stored location by name

🗺️ **Interactive Map**
- Real-time visualization with Leaflet/OpenStreetMap
- Custom markers and edge visualization
- Road geometry integration with OSRM
- Automatic map bounds fitting

🔗 **Graph Management**
- Custom edge creation with manual weights
- Automatic graph building from all location pairs
- Road-realistic distance/time weights via OSRM
- Persistent edge storage

## Project Structure

```
FDSproject/
├── backend/
│   ├── app.py                 # Flask server with API endpoints
│   ├── dijkstra.py            # Python Dijkstra implementation (legacy)
│   ├── java_executor.py       # Java algorithm executor wrapper
│   ├── algorithms/            # Java algorithm implementations
│   │   ├── Graph.java
│   │   ├── DijkstraAlgorithm.java
│   │   ├── BellmanFordAlgorithm.java
│   │   ├── FloydWarshallAlgorithm.java
│   │   ├── LocationHashtable.java
│   │   ├── AlgorithmRunner.java
│   │   ├── compile.bat        # Windows compilation script
│   │   └── compile.sh         # Linux/Mac compilation script
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Main UI
│   ├── script.js              # Frontend logic
│   └── styles.css             # Styling
└── README.md
```

## Prerequisites

- **Python 3.8+**: For the Flask backend
- **Java JDK 11+**: For compiling and running Java algorithms
- **Node.js/npm**: Optional, for frontend development server
- **Google Maps API Key**: For geocoding (optional, falls back to OpenStreetMap)

## Installation & Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Compile Java Algorithms

Navigate to the `backend/algorithms` directory:

**On Windows:**
```bash
cd algorithms
compile.bat
```

**On Linux/Mac:**
```bash
cd algorithms
chmod +x compile.sh
./compile.sh
```

The script will:
- Download the org.json library (if needed)
- Compile all Java source files
- Generate .class files ready for execution

### 3. Start the Backend Server

```bash
cd backend
python app.py
```

The server will start on `http://127.0.0.1:5000`

### 4. Open Frontend

Open `frontend/index.html` in your web browser, or use a local web server:

```bash
# Python 3
python -m http.server 8000

# Or with Node.js
npx http-server
```

Then navigate to `http://localhost:8000/frontend/`

## API Endpoints

### Location Management
- **POST** `/api/locations` - Add a new location
- **GET** `/api/locations/all` - Get all stored locations
- **GET** `/api/locations/<name>` - Get a specific location

### Graph Operations
- **POST** `/api/locations/build-graph` - Build graph from locations
- **POST** `/api/edges` - Add an edge between locations
- **GET** `/api/graph` - Get current graph structure

### Route Finding
- **POST** `/api/route` - Find route using Dijkstra (Python)
- **POST** `/api/algorithms/dijkstra` - Find route using Dijkstra (Python)

### Algorithm Comparison
- **POST** `/api/algorithms/compare` - Compare all three algorithms

### Utility
- **POST** `/api/reset` - Clear all data

## Java Algorithm Classes

### Graph.java
Adjacency list representation supporting both directed and undirected edges.

```java
Graph graph = new Graph(false); // undirected
graph.addEdge("A", "B", 5.0);
```

### DijkstraAlgorithm.java
Greedy shortest path algorithm using priority queue.

**Time Complexity:** O((V + E) log V)  
**Space Complexity:** O(V + E)  
**Best for:** Non-negative weights, single-source shortest path

### BellmanFordAlgorithm.java
Edge relaxation algorithm that handles negative weights and detects negative cycles.

**Time Complexity:** O(V × E)  
**Space Complexity:** O(V)  
**Best for:** Negative weights, negative cycle detection

### FloydWarshallAlgorithm.java
Dynamic programming algorithm for all-pairs shortest paths.

**Time Complexity:** O(V³)  
**Space Complexity:** O(V²)  
**Best for:** All-pairs shortest paths, moderate graph sizes

### LocationHashtable.java
Thread-safe location storage using Java's Hashtable class for persistent storage.

Features:
- Thread-safe operations
- Case-insensitive key lookups
- Timestamp tracking
- Batch retrieval operations

## Usage Guide

### Adding Locations

1. Enter a location name in the "Add Locations" section
2. Click "Add Location"
3. The location will be geocoded and added to both the map and hashtable
4. Location coordinates are saved for later retrieval

### Building the Graph

1. Add at least 2 locations
2. Click "Build Graph (Auto-connect all locations)"
3. The system will create edges using:
   - OSRM for road-realistic distances/times
   - Google Distance Matrix as fallback
   - Haversine distance formula as last resort

### Finding Routes

**Simple Route:**
1. Select start and end locations
2. Click "Find Route"
3. Route will be displayed on the map

**Route with Via Points:**
1. Select start location
2. Select via location (forces path through this point)
3. Select end location
4. Click "Find Route"

### Comparing Algorithms

1. Select start and end locations in the "Compare Algorithms" section
2. Click "Compare All Algorithms"
3. Results panel shows:
   - Execution time for each algorithm
   - Path found by each algorithm
   - Time complexity notation
   - Performance summary

### Retrieving Stored Locations

1. Click "Load All Stored Locations" in the "Stored Locations" section
2. All previously added locations will be displayed with:
   - Coordinates (latitude, longitude)
   - Geocoding source
   - Matched place name (if available)

## Algorithm Performance Examples

For a graph with 50 vertices and 200 edges:

| Algorithm | Time (ms) | Complexity | Best Use Case |
|-----------|-----------|-----------|--------------|
| Dijkstra | 0.5-2.0 | O((V + E) log V) | Single-source, positive weights |
| Bellman-Ford | 5.0-15.0 | O(V × E) | Negative weights, cycle detection |
| Floyd-Warshall | 10.0-50.0 | O(V³) | All-pairs paths |

*Actual times depend on graph structure and system performance*

## Troubleshooting

### "Java compiler (javac) not found"
- **Solution**: Ensure Java JDK (not JRE) is installed and in your PATH
- Verify: Run `javac -version` in terminal

### "JSON library not found"
- **Solution**: Run the compile script again, or manually download from:
  https://github.com/stleary/JSON-java/releases/download/20231013/json-20231013.jar
- Place in `backend/algorithms/` directory

### Backend connection error
- **Solution**: Ensure backend is running on port 5000
- Verify: `python app.py` shows "Running on http://127.0.0.1:5000"

### Locations not geocoding
- **Solution**: Check internet connection
- Verify: Google Maps API key in app.py (optional)
- Fallback: App uses OpenStreetMap Nominatim (free service)

### Algorithm comparison showing errors
- **Solution**: Ensure graph has edges (click "Build Graph")
- Verify: Java compilation successful
- Check: All Java class files (.class) exist in backend/algorithms/

## Configuration

### Google Maps API (Optional)
To use Google Maps instead of OpenStreetMap, add your API key in `backend/app.py`:

```python
GOOGLE_MAPS_API_KEY = "your_api_key_here"
```

### Algorithm Metrics
Change the weight metric when building graphs:
- `metric: "time"` - Road driving time in minutes
- `metric: "distance"` - Road distance in kilometers

## Performance Tips

1. **For Dijkstra**: Best for 1000s of vertices with sparse edges
2. **For Bellman-Ford**: Use only when negative weights are necessary (slower)
3. **For Floyd-Warshall**: Avoid for >100 vertices (cubic time complexity)

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| Python | 3.8 | 3.10+ |
| Java | JDK 11 | JDK 17+ |
| Storage | 100MB | 500MB |

## License

This project is for educational purposes. All algorithms are implemented from first principles.

## Author

Created as a comprehensive demonstration of shortest-path algorithms with real-world integration.

## Future Enhancements

- [ ] A* algorithm for heuristic-based routing
- [ ] Bidirectional Dijkstra implementation
- [ ] Real-time traffic integration
- [ ] Database backend for persistent storage
- [ ] Web socket support for real-time updates
- [ ] Algorithm step-by-step visualization
- [ ] Custom map tile providers
- [ ] Multi-language support

## Support

For issues or questions, check:
1. Terminal output for error messages
2. Browser console (F12 Developer Tools)
3. Flask server logs

---

**Happy route finding! 🗺️✨**
