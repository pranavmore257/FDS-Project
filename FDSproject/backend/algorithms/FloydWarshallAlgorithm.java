import java.util.*;

/**
 * Floyd-Warshall Algorithm Implementation
 * Finds shortest paths between all pairs of vertices
 * Can handle negative edge weights (but not negative cycles)
 * Time Complexity: O(V^3)
 * Space Complexity: O(V^2)
 */
public class FloydWarshallAlgorithm {
    
    public static class FloydWarshallResult {
        public Map<String, Map<String, Double>> distances;
        public Map<String, Map<String, String>> nextVertex;
        public List<String> path;
        public double totalDistance;
        public long executionTimeMs;
        
        public FloydWarshallResult() {
            this.distances = new HashMap<>();
            this.nextVertex = new HashMap<>();
            this.path = new ArrayList<>();
            this.totalDistance = 0;
            this.executionTimeMs = 0;
        }
    }
    
    private Graph graph;
    private List<String> steps;
    
    public FloydWarshallAlgorithm(Graph graph) {
        this.graph = graph;
        this.steps = new ArrayList<>();
    }
    
    /**
     * Find shortest paths between all pairs of vertices
     */
    public FloydWarshallResult findAllPairs() {
        long startTime = System.currentTimeMillis();
        steps.clear();
        
        FloydWarshallResult result = new FloydWarshallResult();
        List<String> vertices = new ArrayList<>(graph.getVertices());
        int n = vertices.size();
        
        // Initialize distance matrix
        Map<String, Map<String, Double>> distances = new HashMap<>();
        Map<String, Map<String, String>> nextVertex = new HashMap<>();
        
        for (String u : vertices) {
            distances.put(u, new HashMap<>());
            nextVertex.put(u, new HashMap<>());
            for (String v : vertices) {
                distances.get(u).put(v, Double.MAX_VALUE);
                nextVertex.get(u).put(v, null);
            }
            distances.get(u).put(u, 0.0);
        }
        
        // Initialize with direct edges
        for (String u : graph.getAdjacencyList().keySet()) {
            for (Graph.Edge edge : graph.getNeighbors(u)) {
                String v = edge.to;
                distances.get(u).put(v, edge.weight);
                nextVertex.get(u).put(v, v);
            }
        }
        
        steps.add("Starting Floyd-Warshall algorithm with " + n + " vertices");
        
        // Floyd-Warshall main algorithm
        for (int k = 0; k < n; k++) {
            String midVertex = vertices.get(k);
            steps.add("Using intermediate vertex: " + midVertex);
            
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
                        steps.add("Updated: " + u + " -> " + v + " via " + midVertex + 
                                " distance: " + viaK);
                    }
                }
            }
        }
        
        result.distances = distances;
        result.nextVertex = nextVertex;
        result.executionTimeMs = System.currentTimeMillis() - startTime;
        
        return result;
    }
    
    /**
     * Find shortest path from source to destination using precomputed distances
     */
    public FloydWarshallResult findShortestPath(String source, String destination) {
        long startTime = System.currentTimeMillis();
        steps.clear();
        
        FloydWarshallResult result = findAllPairs();
        
        // Reconstruct path
        List<String> path = new ArrayList<>();
        String current = source;
        path.add(current);
        
        while (!current.equals(destination)) {
            String next = result.nextVertex.get(current).get(destination);
            if (next == null) {
                steps.add("No path exists from " + source + " to " + destination);
                break;
            }
            current = next;
            path.add(current);
        }
        
        result.path = path;
        result.totalDistance = result.distances.get(source).get(destination) == Double.MAX_VALUE ?
                              -1 : result.distances.get(source).get(destination);
        result.executionTimeMs = System.currentTimeMillis() - startTime;
        
        return result;
    }
    
    public List<String> getSteps() {
        return steps;
    }
}
