# Quick Start Guide - Route Finder with Algorithm Comparison

## What's New ✨

Your application now includes **three powerful shortest-path algorithms in Java** with real-time performance comparison:

### ✅ What Was Implemented

1. **Java Algorithm Implementations**
   - ⚡ **Dijkstra Algorithm** - Fast greedy approach with priority queue
   - 🔄 **Bellman-Ford Algorithm** - Handles negative weights & detects cycles
   - 📊 **Floyd-Warshall Algorithm** - Computes all-pairs shortest paths

2. **Java Location Hashtable Storage**
   - Thread-safe persistent storage of all added locations
   - Retrieve locations by name anytime
   - Stores coordinates, geocode source, and matched place names

3. **Algorithm Performance Comparison UI**
   - Compare execution times side-by-side
   - Display path for each algorithm
   - Show time complexity for each method
   - Performance summary with fastest algorithm highlighted

4. **Enhanced Backend API**
   - `/api/algorithms/compare` - Run all 3 algorithms simultaneously
   - `/api/locations/all` - Retrieve all stored locations
   - `/api/locations/<name>` - Get specific location from hashtable

5. **Improved Frontend UI**
   - New "Compare Algorithms" section with dedicated controls
   - "Stored Locations" section showing hashtable contents
   - Algorithm comparison cards with color-coded performance indicators
   - Real-time execution time display in milliseconds

## Setup (5 Minutes)

### Step 1: Compile Java Algorithms

Navigate to the backend/algorithms directory:

**Windows:**
```bash
cd FDSproject\backend\algorithms
compile.bat
```

**Linux/Mac:**
```bash
cd FDSproject/backend/algorithms
chmod +x compile.sh
./compile.sh
```

✅ Check: You should see messages like "Compilation complete!"

### Step 2: Start the Backend

```bash
cd FDSproject/backend
python app.py
```

✅ Check: You should see "Starting Route Finder Server..." and "Initializing Java algorithm executor..."

### Step 3: Open the Frontend

Open `FDSproject/frontend/index.html` in your web browser

## How to Use

### 1️⃣ Add Locations

- Enter location names (e.g., "Pune", "Katraj", "Baner", "Wakad")
- Locations are automatically geocoded and stored in the hashtable
- Locations appear on the map and in all dropdowns

### 2️⃣ Build a Graph

- Add at least 2 locations
- Click "Build Graph (Auto-connect all locations)"
- The system creates connections using real road data (OSRM)

### 3️⃣ Compare Algorithms

**New Feature!** 🚀

1. In the "Compare Algorithms" section:
   - Select your start location
   - Select your end location
   - Click "Compare All Algorithms"

2. You'll see three algorithm cards showing:
   - **Execution time** (in milliseconds)
   - **Path found** (the route)
   - **Time complexity** (Big O notation)
   - **Path length** (number of stops)

3. Performance summary shows which algorithm was fastest!

### 4️⃣ Retrieve Stored Locations

**New Feature!** 🎯

1. Click "Load All Stored Locations" 
2. All previously added locations appear with:
   - Exact coordinates (latitude, longitude)
   - How they were found (Google, OpenStreetMap, or approximate)
   - Matched place names

## Example Workflow

```
Step 1: Add Locations
├─ "Katraj"
├─ "Baner"
├─ "Wakad"
└─ "Viman Nagar"

Step 2: Build Graph
├─ Click "Build Graph (Auto-connect all locations)"
└─ System creates edges with real road distances

Step 3: Compare Algorithms
├─ Start: Katraj
├─ End: Viman Nagar
├─ Click "Compare All Algorithms"
└─ See which algorithm is fastest!

Step 4: Find Specific Route
├─ Via: Baner (optional, forces path through this point)
├─ Click "Find Route"
└─ Route displays on map
```

## Understanding the Algorithm Comparison

### Example Output

```
Dijkstra:           ⭐ 0.45 ms (Fastest)
Bellman-Ford:       0.89 ms
Floyd-Warshall:     2.34 ms
```

### What Each Algorithm Does

| Algorithm | Speed | When to Use | Special Features |
|-----------|-------|-------------|------------------|
| **Dijkstra** | ⚡ Fastest | Most cases | Priority queue, non-negative |
| **Bellman-Ford** | 🐢 Slow | Negative weights | Detects negative cycles ⚠️ |
| **Floyd-Warshall** | 📊 Slow | All-pairs paths | Computes complete distance matrix |

### Time Complexity

- **Dijkstra**: O((V + E) log V) - Best for sparse graphs
- **Bellman-Ford**: O(V × E) - Linear to graph size
- **Floyd-Warshall**: O(V³) - Cubic, avoid for large graphs

## New API Endpoints

### Compare Algorithms
```
POST /api/algorithms/compare
Body: {"start": "Katraj", "end": "Baner"}
Response: {
  "start": "Katraj",
  "end": "Baner",
  "algorithms": {
    "dijkstra": {
      "distance": 15.4,
      "path": ["Katraj", "Baner"],
      "execution_time_ms": 0.45,
      "complexity": "O((V + E) log V)"
    },
    ...
  },
  "performance_summary": {...}
}
```

### Get All Stored Locations
```
GET /api/locations/all
Response: {
  "count": 4,
  "locations": [
    {
      "name": "Katraj",
      "lat": 18.4521,
      "lng": 73.8141,
      "geocode_source": "google",
      "matched_place": "Katraj, Pune..."
    },
    ...
  ]
}
```

### Get Specific Location
```
GET /api/locations/Katraj
Response: {
  "name": "Katraj",
  "lat": 18.4521,
  "lng": 73.8141,
  "geocode_source": "google",
  "matched_place": "Katraj, Pune..."
}
```

## File Changes Summary

### New Files Created
- `backend/algorithms/Graph.java`
- `backend/algorithms/DijkstraAlgorithm.java`
- `backend/algorithms/BellmanFordAlgorithm.java`
- `backend/algorithms/FloydWarshallAlgorithm.java`
- `backend/algorithms/LocationHashtable.java`
- `backend/algorithms/AlgorithmRunner.java`
- `backend/algorithms/compile.bat`
- `backend/algorithms/compile.sh`
- `backend/java_executor.py`
- `SETUP_INSTRUCTIONS.md`
- `QUICKSTART.md` (this file)

### Modified Files
- `backend/app.py` - Added Java integration & new endpoints
- `frontend/index.html` - Added comparison and location sections
- `frontend/script.js` - Added comparison & retrieval functions
- `frontend/styles.css` - Added styling for algorithm cards

## Troubleshooting

### Issue: "Java compiler not found"
```
Solution: Install Java JDK (not JRE)
- Windows: Download from oracle.com
- Linux: sudo apt-get install openjdk-11-jdk
- Mac: brew install openjdk@11
```

### Issue: Algorithm comparison shows error
```
Solution: Make sure Java compilation succeeded
1. Check if files exist: backend/algorithms/*.class
2. Re-run compile.bat or compile.sh
3. Ensure backend is running (port 5000)
```

### Issue: Locations not being stored
```
Solution: Backend may need restart
1. Stop backend (Ctrl+C)
2. Start again: python app.py
3. Add locations again
```

### Issue: Map not showing
```
Solution: Frontend needs proper server
1. Use: python -m http.server 8000
2. Open: http://localhost:8000/frontend/
3. Or directly open: file:///path/to/frontend/index.html
```

## Performance Tips

- **Fast Results**: Use Dijkstra for most cases (1000s of vertices)
- **Need Negative Weights?**: Use Bellman-Ford (slower, but safer)
- **All Paths Needed?**: Use Floyd-Warshall (up to ~100 vertices)

## Next Steps 🚀

Try these scenarios:

1. **Speed Test**
   - Add 5-10 locations
   - Compare algorithms multiple times
   - Notice Dijkstra is usually fastest

2. **Real-World Routing**
   - Build graph with actual Pune locations
   - Find routes with via points
   - Compare results on map

3. **Performance Analysis**
   - Add many locations (20+)
   - Monitor execution times
   - See where each algorithm excels

## Support

- Check backend terminal for Java compilation/execution errors
- Open browser console (F12) for frontend issues
- Verify file permissions on Linux/Mac
- Ensure firewall doesn't block port 5000

---

**Enjoy exploring shortest-path algorithms! 🗺️⚡**
