# Dijkstra Route Finder - Pune City

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
│   ├── dijkstra.py      # Dijkstra algorithm implementation with data structures
│   └── app.py           # Flask server with API endpoints
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling for the website
│   └── script.js        # JavaScript for map interactions and API calls
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 📚 Data Structures Used

### 1. **Graph (Adjacency List)**
- Implementation: Dictionary of lists
- Structure: `{vertex: [(neighbor, weight), ...]}`
- Used for: Efficient graph representation (O(V + E) space)

### 2. **Priority Queue (Min Heap)**
- Implementation: Python's `heapq` module
- Used for: Efficiently selecting the vertex with minimum distance
- Time Complexity: O(log V) for insertion/extraction

### 3. **Dictionary (Hash Map)**
- Used for: 
  - Distance tracking: O(1) lookup
  - Previous vertex tracking: O(1) for path reconstruction
  - Visited set: O(1) membership check

### 4. **Set**
- Used for: Tracking visited vertices with O(1) average case operations

## 🔧 Algorithm Complexity

- **Time Complexity**: O((V + E) log V)
  - V = number of vertices (locations)
  - E = number of edges (connections between locations)
- **Space Complexity**: O(V + E)
  - Graph: O(V + E)
  - Priority Queue: O(V)
  - Distance/Previous dictionaries: O(V)

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

### `POST /api/locations`
Add a location to the system
```json
{
  "name": "Viman Nagar"
}
```

### `POST /api/edges`
Add a custom edge between locations (optional distance auto-computation)
```json
{
  "from": "Viman Nagar",
  "to": "Hinjawadi",
  "weight": 15.5,  // optional - if omitted, distance will be auto-calculated
  "metric": "distance"  // "distance" (km) or "time" (minutes)
}
```

### `POST /api/locations/build-graph`
Build graph from list of locations
```json
{
  "locations": ["Viman Nagar", "Hinjawadi", "Kothrud"],
  "mode": "all_pairs"  // creates edges between all location pairs
}
```

### `POST /api/route`
Find shortest route using Dijkstra's algorithm
```json
{
  "start": "Viman Nagar",
  "end": "Hinjawadi"
}
```

### `GET /api/graph`
Get current graph structure

## 🧮 Algorithm Implementation Details

### Dijkstra's Algorithm Steps:

1. **Initialize**:
   - Distance dictionary: All vertices set to infinity except start (0)
   - Priority queue: Add start vertex with distance 0
   - Previous dictionary: Track path reconstruction

2. **Main Loop**:
   - Extract vertex with minimum distance from priority queue
   - Mark as visited
   - If reached destination, reconstruct and return path
   - For each unvisited neighbor:
     - Calculate new distance = current distance + edge weight
     - If new distance < known distance, update and add to queue

3. **Path Reconstruction**:
   - Start from end vertex
   - Follow previous pointers back to start
   - Reverse to get path from start to end

## 🎨 Features in Detail

- **Graph Representation**: Adjacency list for efficient edge traversal
- **Heap-based Priority Queue**: Ensures O(log V) operations for vertex selection
- **Bidirectional Edges**: Graph supports two-way travel between locations
- **Real-time Route Calculation**: Uses actual Google Maps driving times
- **Visual Feedback**: Color-coded markers (green=start, red=end, yellow=waypoints)

## 🛠️ Technologies Used

- **Backend**: Python, Flask, Dijkstra's Algorithm
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: Google Maps JavaScript API, Google Geocoding API, Google Distance Matrix API
- **Data Structures**: Graph, Priority Queue (Heap), Dictionary, Set

## 📝 Notes

- The algorithm finds the shortest path based on **travel time**, not distance
- All locations are automatically geocoded to Pune, Maharashtra, India
- The graph is built dynamically based on user input
- Edge weights represent driving time in minutes

## 🔒 Security Note

The Google Maps API key is included in the code. For production use, consider:
- Using environment variables
- Implementing API key restrictions in Google Cloud Console
- Using a backend proxy to hide the API key from frontend

## 📄 License

This is an educational project for Data Structures and Algorithms demonstration.

## 👨‍💻 Author

Created as a DSA project demonstrating Dijkstra's algorithm with practical application in route finding.


