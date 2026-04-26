# DSA Algorithms and Hashtable Implementation in FDS Project

## Table of Contents
1. [Project Overview](#project-overview)
2. [Hashtable Implementation](#hashtable-implementation)
3. [Graph Data Structure](#graph-data-structure)
4. [Shortest Path Algorithms](#shortest-path-algorithms)
5. [Algorithm Integration](#algorithm-integration)
6. [Performance Analysis](#performance-analysis)
7. [Real-World Examples](#real-world-examples)

## Project Overview

The FDS (File System and Data Structures) Project implements a comprehensive route finding system that demonstrates practical applications of fundamental Data Structures and Algorithms (DSA). The project combines Java-based algorithm implementations with a Python Flask backend to create a robust location-based service.

### Key Components:
- **LocationHashtable**: Persistent storage for location data
- **Graph Data Structure**: Adjacency list and matrix representations
- **Three Shortest Path Algorithms**: Dijkstra, Bellman-Ford, Floyd-Warshall
- **Hybrid Architecture**: Java algorithms + Python backend

## Hashtable Implementation

### Java Implementation (`LocationHashtable.java`)

The project uses Java's built-in `Hashtable` class for thread-safe location storage:

```java
public class LocationHashtable implements Serializable {
    private Hashtable<String, Location> locations;
    
    public static class Location implements Serializable {
        public String name;
        public double latitude;
        public double longitude;
        public String geocodeSource;
        public String matchedPlace;
        public long timestamp;
    }
}
```

### Key Hashtable Operations:

1. **Add Location**:
```java
public synchronized void addLocation(String name, double latitude, double longitude,
                                   String geocodeSource, String matchedPlace) {
    Location loc = new Location(name, latitude, longitude, geocodeSource, matchedPlace);
    locations.put(name.toLowerCase(), loc);  // Case-insensitive key
}
```

2. **Retrieve Location**:
```java
public synchronized Location getLocation(String name) {
    return locations.get(name.toLowerCase());
}
```

3. **Check Existence**:
```java
public synchronized boolean hasLocation(String name) {
    return locations.containsKey(name.toLowerCase());
}
```

### Python Equivalent (`app.py`)

The Python backend provides a similar implementation using `OrderedDict`:

```python
class LocationHashtable:
    """Thread-safe location storage using OrderedDict"""
    def __init__(self):
        self.locations = OrderedDict()
    
    def add(self, name, lat, lng, geocode_source, matched_place):
        key = name.lower()
        self.locations[key] = {
            'name': name,
            'lat': lat,
            'lng': lng,
            'geocode_source': geocode_source,
            'matched_place': matched_place,
            'timestamp': hash(name)
        }
```

### Hashtable Benefits in This Project:

1. **O(1) Average Time Complexity**: Fast lookups for location data
2. **Thread Safety**: Synchronized methods prevent concurrent access issues
3. **Case Insensitivity**: All keys converted to lowercase for consistent access
4. **Serialization**: Supports persistent storage across application restarts

## Graph Data Structure

### Dual Representation Approach

The project implements a hybrid graph representation to support different algorithms efficiently:

```java
public class Graph {
    private Map<String, List<Edge>> adjacencyList;  // For Dijkstra/Bellman-Ford
    private Set<String> vertices;
    private Map<String, Map<String, Double>> adjMatrix;  // For Floyd-Warshall
    private boolean isDirected;
}
```

### Edge Class:

```java
public static class Edge {
    public String to;
    public double weight;
    
    public Edge(String to, double weight) {
        this.to = to;
        this.weight = weight;
    }
}
```

### Graph Construction Example:

```java
// Adding edges to the graph
graph.addEdge("Pune", "Mumbai", 150.5);  // 150.5 km
graph.addEdge("Mumbai", "Nashik", 165.2);
graph.addEdge("Pune", "Nashik", 210.8);
```

### Why Dual Representation?

1. **Adjacency List**: Efficient for sparse graphs (O(V + E) space)
2. **Adjacency Matrix**: Required for Floyd-Warshall algorithm (O(V²) space)
3. **Flexibility**: Supports both directed and undirected graphs

## Shortest Path Algorithms

### 1. Dijkstra's Algorithm

**Purpose**: Find shortest path from source to all vertices with non-negative weights.

**Time Complexity**: O((V + E) log V) using priority queue

**Key Implementation**:

```java
public DijkstraResult findShortestPath(String source, String destination) {
    // Priority queue: (distance, vertex)
    PriorityQueue<AbstractMap.SimpleEntry<Double, String>> pq = new PriorityQueue<>(
            Comparator.comparingDouble(AbstractMap.SimpleEntry::getKey)
    );
    
    // Initialize distances
    for (String vertex : graph.getVertices()) {
        distances.put(vertex, Double.MAX_VALUE);
    }
    distances.put(source, 0.0);
    
    while (!pq.isEmpty()) {
        AbstractMap.SimpleEntry<Double, String> current = pq.poll();
        String currentVertex = current.getValue();
        
        // Relax edges
        for (Graph.Edge edge : graph.getNeighbors(currentVertex)) {
            String neighbor = edge.to;
            double newDist = currentDist + edge.weight;
            
            if (newDist < distances.get(neighbor)) {
                distances.put(neighbor, newDist);
                previousVertex.put(neighbor, currentVertex);
                pq.offer(new AbstractMap.SimpleEntry<>(newDist, neighbor));
            }
        }
    }
}
```

**When to Use**: 
- Graphs with non-negative edge weights
- Single-source shortest path
- Need fastest performance for sparse graphs

### 2. Bellman-Ford Algorithm

**Purpose**: Find shortest path from source to all vertices, handles negative weights.

**Time Complexity**: O(V × E)

**Key Implementation**:

```java
public BellmanFordResult findShortestPath(String source, String destination) {
    // Relax edges |V| - 1 times
    int vertexCount = graph.getVertices().size();
    for (int i = 0; i < vertexCount - 1; i++) {
        // For each edge
        for (String u : graph.getAdjacencyList().keySet()) {
            for (Graph.Edge edge : graph.getNeighbors(u)) {
                String v = edge.to;
                double weight = edge.weight;
                
                if (distances.get(u) != Double.MAX_VALUE && 
                    distances.get(u) + weight < distances.get(v)) {
                    distances.put(v, distances.get(u) + weight);
                    previousVertex.put(v, u);
                }
            }
        }
    }
    
    // Check for negative cycles
    for (String u : graph.getAdjacencyList().keySet()) {
        for (Graph.Edge edge : graph.getNeighbors(u)) {
            String v = edge.to;
            double weight = edge.weight;
            
            if (distances.get(u) != Double.MAX_VALUE && 
                distances.get(u) + weight < distances.get(v)) {
                result.hasNegativeCycle = true;
                result.errorMessage = "Negative cycle detected!";
            }
        }
    }
}
```

**When to Use**:
- Graphs with negative edge weights
- Need to detect negative cycles
- Single-source shortest path with negative weights

### 3. Floyd-Warshall Algorithm

**Purpose**: Find shortest paths between all pairs of vertices.

**Time Complexity**: O(V³)

**Key Implementation**:

```java
public FloydWarshallResult findAllPairs() {
    // Initialize distance matrix
    for (String u : vertices) {
        for (String v : vertices) {
            distances.get(u).put(v, Double.MAX_VALUE);
            nextVertex.get(u).put(v, null);
        }
        distances.get(u).put(u, 0.0);
    }
    
    // Floyd-Warshall main algorithm
    for (int k = 0; k < n; k++) {
        String midVertex = vertices.get(k);
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                String u = vertices.get(i);
                String v = vertices.get(j);
                
                double directDist = distances.get(u).get(v);
                double viaK = distances.get(u).get(midVertex) + 
                             distances.get(midVertex).get(v);
                
                if (viaK < directDist) {
                    distances.get(u).put(v, viaK);
                    nextVertex.get(u).put(v, nextVertex.get(u).get(midVertex));
                }
            }
        }
    }
}
```

**When to Use**:
- Need all-pairs shortest paths
- Dense graphs
- Graphs with negative weights (but no negative cycles)

## Algorithm Integration

### Java-Python Bridge

The project uses a sophisticated integration mechanism:

1. **Java Algorithm Runner** (`AlgorithmRunner.java`):
```java
public static void main(String[] args) {
    String jsonInput = args[0];
    JSONObject input = new JSONObject(jsonInput);
    
    // Parse input and build graph
    Graph graph = new Graph(false);
    // ... graph construction
    
    // Run all algorithms
    DijkstraAlgorithm dijkstra = new DijkstraAlgorithm(graph);
    BellmanFordAlgorithm bellmanFord = new BellmanFordAlgorithm(graph);
    FloydWarshallAlgorithm floydWarshall = new FloydWarshallAlgorithm(graph);
    
    // Output JSON results
    System.out.println(results.toString());
}
```

2. **Python Executor** (`java_executor.py`):
```python
def get_executor():
    """Get the appropriate Java executor based on OS"""
    if platform.system() == "Windows":
        return "java -cp \".;json-20231013.jar\" AlgorithmRunner"
    else:
        return "java -cp \".:json-20231013.jar\" AlgorithmRunner"
```

3. **Flask Integration** (`app.py`):
```python
@app.route('/run_algorithms', methods=['POST'])
def run_algorithms():
    data = request.get_json()
    
    # Prepare input for Java
    input_data = {
        'vertices': list(vertices),
        'edges': [{'from': edge[0], 'to': edge[1], 'weight': edge[2]} 
                 for edge in edges],
        'source': source,
        'destination': destination
    }
    
    # Execute Java algorithms
    cmd = f"{get_executor()} '{json.dumps(input_data)}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return jsonify(json.loads(result.stdout))
```

## Performance Analysis

### Algorithm Comparison

| Algorithm | Time Complexity | Space Complexity | Negative Weights | Use Case |
|-----------|----------------|------------------|------------------|----------|
| Dijkstra | O((V + E) log V) | O(V) | No | Single-source, fastest |
| Bellman-Ford | O(V × E) | O(V) | Yes | Single-source with negatives |
| Floyd-Warshall | O(V³) | O(V²) | Yes | All-pairs shortest path |

### Real Performance Metrics

From the project's implementation:

```java
// Execution time tracking
long startTime = System.currentTimeMillis();
// ... algorithm execution
result.executionTimeMs = System.currentTimeMillis() - startTime;
```

### Memory Usage Analysis

1. **Hashtable Storage**: O(n) where n is number of locations
2. **Graph Storage**: O(V + E) for adjacency list, O(V²) for adjacency matrix
3. **Algorithm Memory**: 
   - Dijkstra: O(V) for priority queue
   - Bellman-Ford: O(V) for distance array
   - Floyd-Warshall: O(V²) for distance matrix

## Real-World Examples

### Example 1: Pune-Mumbai Route Finding

**Input Data**:
```json
{
  "vertices": ["Pune", "Mumbai", "Nashik", "Lonavala"],
  "edges": [
    {"from": "Pune", "to": "Mumbai", "weight": 150.5},
    {"from": "Pune", "to": "Lonavala", "weight": 64.2},
    {"from": "Lonavala", "to": "Mumbai", "weight": 83.1},
    {"from": "Pune", "to": "Nashik", "weight": 210.8},
    {"from": "Nashik", "to": "Mumbai", "weight": 165.2}
  ],
  "source": "Pune",
  "destination": "Mumbai"
}
```

**Dijkstra Result**:
```json
{
  "algorithm": "Dijkstra",
  "distance": 147.3,
  "path": ["Pune", "Lonavala", "Mumbai"],
  "execution_time_ms": 2,
  "steps": [
    "Starting Dijkstra from: Pune",
    "Visiting: Pune with distance: 0.0",
    "Updated: Mumbai to distance: 150.5",
    "Updated: Lonavala to distance: 64.2",
    "Updated: Nashik to distance: 210.8",
    "Visiting: Lonavala with distance: 64.2",
    "Updated: Mumbai to distance: 147.3"
  ]
}
```

### Example 2: Location Hashtable Usage

**Adding Locations**:
```java
LocationHashtable hashtable = new LocationHashtable();

// Add Pune
hashtable.addLocation("Pune", 18.5204, 73.8567, "Google Maps", "Pune, Maharashtra");

// Add Mumbai
hashtable.addLocation("Mumbai", 19.0760, 72.8777, "Google Maps", "Mumbai, Maharashtra");

// Retrieve location
Location pune = hashtable.getLocation("Pune");
System.out.println(pune.toString());
// Output: Location{name='Pune', lat=18.5204, lng=73.8567, source='Google Maps', matched='Pune, Maharashtra'}
```

### Example 3: Negative Weight Detection

**Graph with Negative Edge**:
```java
// Add negative weight edge (representing discount/toll reduction)
graph.addEdge("CityA", "CityB", -10.0);

// Bellman-Ford will detect if this creates a negative cycle
BellmanFordResult result = bellmanFord.findShortestPath("CityA", "CityC");
if (result.hasNegativeCycle) {
    System.out.println("Negative cycle detected: " + result.errorMessage);
}
```

### Example 4: All-Pairs Shortest Path

**Floyd-Warshall for Multiple Destinations**:
```java
FloydWarshallAlgorithm floydWarshall = new FloydWarshallAlgorithm(graph);
FloydWarshallResult allPairs = floydWarshall.findAllPairs();

// Get distance from any source to any destination
double distance = allPairs.distances.get("Pune").get("Mumbai");
List<String> path = floydWarshall.reconstructPath("Pune", "Mumbai");
```

## Best Practices and Design Patterns

### 1. **Synchronization**
```java
public synchronized void addLocation(...) {
    // Thread-safe operations
}
```

### 2. **Serialization Support**
```java
public class LocationHashtable implements Serializable {
    private static final long serialVersionUID = 1L;
}
```

### 3. **Result Objects**
```java
public static class DijkstraResult {
    public Map<String, Double> distances;
    public Map<String, String> previousVertex;
    public List<String> path;
    public double totalDistance;
    public long executionTimeMs;
}
```

### 4. **Error Handling**
```java
try {
    // Algorithm execution
} catch (Exception e) {
    JSONObject error = new JSONObject();
    error.put("error", e.getMessage());
    System.out.println(error.toString());
}
```

## Conclusion

This project demonstrates a sophisticated implementation of fundamental DSA concepts in a real-world application. The combination of hashtable-based location storage, multiple graph representations, and three different shortest path algorithms provides a comprehensive learning platform for understanding:

1. **Data Structure Selection**: Choosing the right structure for specific use cases
2. **Algorithm Trade-offs**: Understanding when to use each algorithm
3. **System Integration**: Combining different programming languages effectively
4. **Performance Optimization**: Implementing efficient solutions with proper complexity analysis

The project serves as an excellent example of how theoretical DSA concepts translate into practical, scalable solutions for location-based services and route optimization problems.

---

**File Locations in Project:**
- `FDSproject/backend/algorithms/LocationHashtable.java` - Main hashtable implementation
- `FDSproject/backend/algorithms/Graph.java` - Graph data structure
- `FDSproject/backend/algorithms/DijkstraAlgorithm.java` - Dijkstra implementation
- `FDSproject/backend/algorithms/BellmanFordAlgorithm.java` - Bellman-Ford implementation
- `FDSproject/backend/algorithms/FloydWarshallAlgorithm.java` - Floyd-Warshall implementation
- `FDSproject/backend/algorithms/AlgorithmRunner.java` - Java-Python integration
- `FDSproject/backend/app.py` - Python Flask backend with hashtable implementation
