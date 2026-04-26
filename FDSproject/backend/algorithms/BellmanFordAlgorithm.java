import java.util.*;

/**
 * Bellman-Ford Algorithm Implementation
 * Finds shortest path from source to all other vertices
 * Can handle negative edge weights (unlike Dijkstra)
 * Detects negative cycles
 * Time Complexity: O(V * E)
 */
public class BellmanFordAlgorithm {
    
    public static class BellmanFordResult {
        public Map<String, Double> distances;
        public Map<String, String> previousVertex;
        public List<String> path;
        public double totalDistance;
        public long executionTimeMs;
        public boolean hasNegativeCycle;
        public String errorMessage;
        
        public BellmanFordResult() {
            this.distances = new HashMap<>();
            this.previousVertex = new HashMap<>();
            this.path = new ArrayList<>();
            this.totalDistance = 0;
            this.executionTimeMs = 0;
            this.hasNegativeCycle = false;
            this.errorMessage = "";
        }
    }
    
    private Graph graph;
    private List<String> steps;
    
    public BellmanFordAlgorithm(Graph graph) {
        this.graph = graph;
        this.steps = new ArrayList<>();
    }
    
    /**
     * Find shortest path from source to destination
     */
    public BellmanFordResult findShortestPath(String source, String destination) {
        long startTime = System.currentTimeMillis();
        steps.clear();
        
        BellmanFordResult result = new BellmanFordResult();
        Map<String, Double> distances = new HashMap<>();
        Map<String, String> previousVertex = new HashMap<>();
        
        // Initialize distances
        for (String vertex : graph.getVertices()) {
            distances.put(vertex, Double.MAX_VALUE);
            previousVertex.put(vertex, null);
        }
        distances.put(source, 0.0);
        
        steps.add("Starting Bellman-Ford from: " + source);
        
        // Relax edges |V| - 1 times
        int vertexCount = graph.getVertices().size();
        for (int i = 0; i < vertexCount - 1; i++) {
            steps.add("Iteration " + (i + 1) + " of " + (vertexCount - 1));
            
            // For each edge
            for (String u : graph.getAdjacencyList().keySet()) {
                for (Graph.Edge edge : graph.getNeighbors(u)) {
                    String v = edge.to;
                    double weight = edge.weight;
                    
                    if (distances.get(u) != Double.MAX_VALUE && 
                        distances.get(u) + weight < distances.get(v)) {
                        distances.put(v, distances.get(u) + weight);
                        previousVertex.put(v, u);
                        steps.add("Relaxed edge: " + u + " -> " + v + 
                                " distance: " + distances.get(v));
                    }
                }
            }
        }
        
        // Check for negative cycles
        steps.add("Checking for negative cycles...");
        for (String u : graph.getAdjacencyList().keySet()) {
            for (Graph.Edge edge : graph.getNeighbors(u)) {
                String v = edge.to;
                double weight = edge.weight;
                
                if (distances.get(u) != Double.MAX_VALUE && 
                    distances.get(u) + weight < distances.get(v)) {
                    result.hasNegativeCycle = true;
                    result.errorMessage = "Negative cycle detected in the graph!";
                    steps.add("NEGATIVE CYCLE DETECTED!");
                    break;
                }
            }
            if (result.hasNegativeCycle) break;
        }
        
        // Build path
        List<String> path = new ArrayList<>();
        String current = destination;
        while (current != null) {
            path.add(0, current);
            current = previousVertex.get(current);
        }
        
        result.distances = distances;
        result.previousVertex = previousVertex;
        result.path = path;
        result.totalDistance = distances.get(destination) == Double.MAX_VALUE ? 
                              -1 : distances.get(destination);
        result.executionTimeMs = System.currentTimeMillis() - startTime;
        
        return result;
    }
    
    public List<String> getSteps() {
        return steps;
    }
}
