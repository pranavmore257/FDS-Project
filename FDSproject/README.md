

A Data Structures and Algorithms project implementing Dijkstra's algorithm to find the shortest route in Pune city using time as the weight metric.

## 🎯 Features

- **Interactive Map**: Google Maps integration showing Pune city
- **Multiple Locations**: Add multiple locations to create a route network
- **Shortest Path**: Find the shortest route based on travel time using Dijkstra's algorithm
- **Real-time Data**: Uses Google Maps API to get real coordinates and driving times
- **Visual Route Display**: Shows the calculated route on the map with markers

## 🏗️ Project Structure

```
FDSproject/
├── backend/
│   ├── app.py                    # Flask server with API endpoints
│   ├── dijkstra.py               # Python Dijkstra implementation
│   ├── java_executor.py          # Java algorithm executor
│   ├── verify_setup.py           # Verification utilities
│   └── algorithms/
│       ├── AlgorithmRunner.java   # Main Java entry point
│       ├── DijkstraAlgorithm.java # Dijkstra in Java
│       ├── BellmanFordAlgorithm.java  # Bellman-Ford in Java
│       ├── FloydWarshallAlgorithm.java  # Floyd-Warshall in Java
│       ├── Graph.java            # Graph data structure
│       ├── LocationHashtable.java # Thread-safe location storage
│       └── json-20231013.jar     # JSON library for Java
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling for the website
│   └── script.js        # JavaScript for map interactions and API calls
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 📚 Data Structures Used

### 1. **Graph (Adjacency List)**
- Implementation: Dictionary of lists (Python) and HashMap in Java
- Structure: `{vertex: [(neighbor, weight), ...]}`
- Used for: Efficient graph representation (O(V + E) space)

### 2. **Priority Queue (Min Heap)**
- Implementation: Python's `heapq` module, Java's `PriorityQueue`
- Used for: Efficiently selecting the vertex with minimum distance (Dijkstra)
- Time Complexity: O(log V) for insertion/extraction

### 3. **Dictionary / HashMap (Hash Map)**
- Used for: 
  - Distance tracking: O(1) lookup
  - Previous vertex tracking: O(1) for path reconstruction
  - Visited set: O(1) membership check

### 4. **LocationHashtable (Thread-safe Hashtable)**
- Thread-safe storage for location data
- Supports: Geocoding data, coordinates, and metadata caching
- Methods: addLocation, getLocation, hasLocation, removeLocation, getAllLocations
- Used for: Persistent location management across algorithm runs

### 5. **Set**
- Used for: Tracking visited vertices with O(1) average case operations

## 🔧 Algorithm Complexity

### Dijkstra's Algorithm
- **Time Complexity**: O((V + E) log V) with binary heap
- **Space Complexity**: O(V + E)
- **Best For**: Non-negative weights, single-source shortest path

### Bellman-Ford Algorithm
- **Time Complexity**: O(V × E)
- **Space Complexity**: O(V)
- **Best For**: Negative edge weights, single-source shortest path, negative cycle detection
- **Advantage**: Can detect negative cycles

### Floyd-Warshall Algorithm
- **Time Complexity**: O(V³)
- **Space Complexity**: O(V²)
- **Best For**: All-pairs shortest paths, dense graphs
- **Advantage**: Finds shortest paths between all pairs in one run

**Variable Definitions:**
- V = number of vertices (locations)
- E = number of edges (connections between locations)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Google Maps API Key (already included in code)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend Server

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### Step 3: Open the Frontend

1. Open `frontend/index.html` in a web browser
2. Or use a local server:
   ```bash
   # Using Python's built-in server
   cd frontend
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser

## 📖 How to Use

1. **Add Locations**: 
   - Type a location name in Pune (e.g., "Viman Nagar", "Hinjawadi", "Kothrud")
   - Click "Add Location" or press Enter
   - Add multiple locations to create your network

2. **Create Connections** (Choose one option):
   
   **Option A: Manual Edges**
   - Select "From" and "To" locations from dropdowns
   - Optionally enter a distance (km) - if left blank, distance will be auto-calculated using Google Maps
   - Click "Add Edge"
   
   **Option B: Auto-Build Graph**
   - After adding at least 2 locations, click "Build Graph (Auto-connect all locations)"
   - This automatically calculates driving distances between all location pairs using Google Maps API

3. **Find Route**:
   - Select a start point from the dropdown
   - Select an end point from the dropdown  
   - Click "Find Route"
   - The shortest route will be calculated using Dijkstra's algorithm and displayed on the map

4. **Clear All**: Click "Clear All" to reset and start fresh

## 🔌 API Endpoints

### Location Management

#### `POST /api/locations`
Add a location to the system
```json
{
  "name": "Viman Nagar"
}
```

#### `GET /api/locations/all`
Retrieve all stored locations from hashtable
**Response:**
```json
{
  "locations": [
    {
      "name": "Viman Nagar",
      "latitude": 18.5595,
      "longitude": 73.9278,
      "geocodeSource": "google",
      "matchedPlace": "Viman Nagar, Pune"
    }
  ]
}
```

#### `GET /api/locations/<name>`
Retrieve a specific location by name

### Graph Management

#### `POST /api/edges`
Add a custom edge between locations (optional distance auto-computation)
```json
{
  "from": "Viman Nagar",
  "to": "Hinjawadi",
  "weight": 15.5,  // optional - if omitted, distance will be auto-calculated
  "metric": "distance"  // "distance" (km) or "time" (minutes)
}
```

#### `POST /api/locations/build-graph`
Build graph from list of locations
```json
{
  "locations": ["Viman Nagar", "Hinjawadi", "Kothrud"],
  "mode": "all_pairs"  // creates edges between all location pairs
}
```

#### `GET /api/graph`
Get current graph structure

### Pathfinding Endpoints

#### `POST /api/route`
Find shortest route using Python Dijkstra's algorithm
```json
{
  "start": "Viman Nagar",
  "end": "Hinjawadi"
}
```

#### `POST /api/algorithms/compare`
Run all three Java algorithms and compare results
```json
{
  "start": "Viman Nagar",
  "end": "Hinjawadi"
}
```
**Response:**
```json
{
  "dijkstra": {
    "path": ["Viman Nagar", "...", "Hinjawadi"],
    "distance": 45.5,
    "executionTimeMs": 2,
    "algorithm": "Dijkstra"
  },
  "bellmanFord": {
    "path": [...],
    "distance": 45.5,
    "executionTimeMs": 5,
    "hasNegativeCycle": false
  },
  "floydWarshall": {
    "allPairs": {...},
    "distance": 45.5,
    "executionTimeMs": 8
  }
}
```

#### `POST /api/algorithms/dijkstra`
Run only Dijkstra's algorithm (Java version)

#### `POST /api/algorithms/bellmanford`
Run only Bellman-Ford algorithm

#### `POST /api/algorithms/floydwarshall`
Run only Floyd-Warshall algorithm

## 🧮 Algorithm Implementation Details

### 1. Dijkstra's Algorithm

**Steps:**
1. Initialize distance dictionary (all infinity except start = 0)
2. Add start vertex to priority queue
3. While queue not empty:
   - Extract vertex with minimum distance
   - Mark as visited
   - For each unvisited neighbor:
     - Calculate new distance = current distance + edge weight
     - If new distance < known distance, update and add to queue
4. Reconstruct path by following previous pointers

**Characteristics:**
- Greedy algorithm
- Cannot handle negative edge weights
- Optimal for non-negative weighted graphs
- Implemented in both Python and Java

### 2. Bellman-Ford Algorithm

**Steps:**
1. Initialize distances to all vertices as infinity (source = 0)
2. Relax all edges V-1 times:
   - For each edge (u, v):
     - If distance[u] + weight(u,v) < distance[v]:
       - Update distance[v]
3. Check for negative cycles:
   - For each edge (u, v):
     - If distance[u] + weight(u,v) < distance[v]: negative cycle detected

**Characteristics:**
- Can handle negative edge weights
- Detects negative cycles
- Slower than Dijkstra for non-negative weights
- More versatile for real-world scenarios

### 3. Floyd-Warshall Algorithm

**Steps:**
1. Initialize distance matrix:
   - Distance[i][i] = 0
   - Distance[i][j] = weight of edge or infinity
2. For k = 1 to V:
   - For i = 1 to V:
     - For j = 1 to V:
       - Distance[i][j] = min(Distance[i][j], Distance[i][k] + Distance[k][j])
3. Return complete distance matrix

**Characteristics:**
- Computes all-pairs shortest paths in one run
- Handles negative edges (but not negative cycles)
- Space-intensive but efficient for dense graphs
- Useful for comparing routes between all location pairs

### 4. LocationHashtable

**Features:**
- Thread-safe location storage using Java's Hashtable
- Caches geocoded location data (coordinates, source, matched place)
- O(1) average case operations for add/get/remove
- Supports bulk retrieval of all locations

**Data Stored per Location:**
- Name (normalized to lowercase for case-insensitive lookup)
- Latitude/Longitude coordinates
- Geocode source (Google Maps, OpenStreetMap, etc.)
- Matched place name from geocoding service
- Timestamp of when location was added

## 🎨 Features in Detail

- **Graph Representation**: Adjacency list for efficient edge traversal
- **Heap-based Priority Queue**: Ensures O(log V) operations for vertex selection
- **Bidirectional Edges**: Graph supports two-way travel between locations
- **Real-time Route Calculation**: Uses actual Google Maps driving times
- **Visual Feedback**: Color-coded markers (green=start, red=end, yellow=waypoints)

## 🛠️ Technologies Used

### Backend
- **Python 3.7+**: Flask, Flask-CORS
- **Java**: Multiple algorithms (Dijkstra, Bellman-Ford, Floyd-Warshall)
- **Algorithms**: Graph traversal, shortest path, all-pairs shortest path
- **Data Structures**: Graph (adjacency list), Priority Queue, HashMap, Hashtable

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with grid layouts
- **JavaScript**: Vanilla JS (700+ lines), event handling, API communication

### External APIs & Libraries
- **Google Maps API**: Geocoding, Distance Matrix, Map visualization
- **OpenStreetMap Nominatim**: Alternative geocoding
- **OSRM (Open Source Routing Machine)**: Real road distance data
- **JSON library**: Java JSON processing (json-20231013.jar)

### Integration
- **IPC**: Python subprocess to Java JVM communication
- **Data Format**: JSON for all inter-process communication
- **Threading**: Thread-safe hashtable for concurrent location access

## 📝 Notes

### Algorithm Selection
- **Dijkstra**: Best for general use, faster for non-negative weights
- **Bellman-Ford**: Use when negative edge weights are possible or for cycle detection
- **Floyd-Warshall**: Use when you need all-pairs shortest paths (comparing all location combinations)

### Data & Execution
- The algorithm finds the shortest path based on **travel time**, not distance
- All locations are automatically geocoded to Pune, Maharashtra, India
- The graph is built dynamically based on user input
- Edge weights represent driving time in minutes (or distance in km)
- Java algorithms run in a separate JVM instance for performance isolation
- LocationHashtable provides persistent caching across requests

### Performance
- Dijkstra (Python): O((V + E) log V) - Optimal for single-pair paths
- Bellman-Ford (Java): O(V × E) - Good for negative weights
- Floyd-Warshall (Java): O(V³) - Best for all-pairs comparison
- Execution times are measured and returned in API responses

## 🔒 Security & Best Practices

### API Key Management
The Google Maps API key is included in the code. For production use, consider:
- Using environment variables for sensitive credentials
- Implementing API key restrictions in Google Cloud Console
- Using a backend proxy to hide the API key from frontend

### Java Security
- LocationHashtable uses synchronized methods for thread-safety
- Each algorithm run is isolated in its own JVM process
- Input validation on all graph operations

### Frontend Security
- CORS enabled for cross-origin requests
- Input sanitization for location names
- Error handling for API failures

## 📄 License

This is an educational project for Data Structures and Algorithms demonstration.

## 👨‍💻 Author

Created as a DSA project demonstrating Dijkstra's algorithm with practical application in route finding.


