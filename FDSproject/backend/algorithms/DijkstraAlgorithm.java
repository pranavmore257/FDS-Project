import java.util.*;

/**
 * Dijkstra's Algorithm Implementation
 * Finds shortest path from a source to all other vertices
 * Uses Priority Queue (Min-Heap) for efficiency
 * Time Complexity: O((V + E) log V)
 */
public class DijkstraAlgorithm {
    
    public static class DijkstraResult {
        public Map<String, Double> distances;
        public Map<String, String> previousVertex;
        public List<String> path;
        public double totalDistance;
        public long executionTimeMs;
        
        public DijkstraResult() {
            this.distances = new HashMap<>();
            this.previousVertex = new HashMap<>();
            this.path = new ArrayList<>();
            this.totalDistance = 0;
            this.executionTimeMs = 0;
        }
    }
    
    private Graph graph;
    private List<String> steps; // For visualization
    
    public DijkstraAlgorithm(Graph graph) {
        this.graph = graph;
        this.steps = new ArrayList<>();
    }
    
    /**
     * Find shortest path from source to destination
     */
    public DijkstraResult findShortestPath(String source, String destination) {
        long startTime = System.currentTimeMillis();
        steps.clear();
        
        DijkstraResult result = new DijkstraResult();
        Map<String, Double> distances = new HashMap<>();
        Map<String, String> previousVertex = new HashMap<>();
        Set<String> visited = new HashSet<>();
        
        // Initialize distances
        for (String vertex : graph.getVertices()) {
            distances.put(vertex, Double.MAX_VALUE);
            previousVertex.put(vertex, null);
        }
        distances.put(source, 0.0);
        
        // Priority queue: (distance, vertex)
        PriorityQueue<AbstractMap.SimpleEntry<Double, String>> pq = new PriorityQueue<>(
                Comparator.comparingDouble(AbstractMap.SimpleEntry::getKey)
        );
        pq.offer(new AbstractMap.SimpleEntry<>(0.0, source));
        
        steps.add("Starting Dijkstra from: " + source);
        
        while (!pq.isEmpty()) {
            AbstractMap.SimpleEntry<Double, String> current = pq.poll();
            double currentDist = current.getKey();
            String currentVertex = current.getValue();
            
            if (visited.contains(currentVertex)) {
                continue;
            }
            
            visited.add(currentVertex);
            steps.add("Visiting: " + currentVertex + " with distance: " + currentDist);
            
            // If reached destination, we can stop
            if (currentVertex.equals(destination)) {
                break;
            }
            
            // Check all neighbors
            for (Graph.Edge edge : graph.getNeighbors(currentVertex)) {
                String neighbor = edge.to;
                double newDist = currentDist + edge.weight;
                
                if (newDist < distances.get(neighbor)) {
                    distances.put(neighbor, newDist);
                    previousVertex.put(neighbor, currentVertex);
                    pq.offer(new AbstractMap.SimpleEntry<>(newDist, neighbor));
                    steps.add("Updated: " + neighbor + " to distance: " + newDist);
                }
            }
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
        result.totalDistance = distances.get(destination);
        result.executionTimeMs = System.currentTimeMillis() - startTime;
        
        return result;
    }
    
    public List<String> getSteps() {
        return steps;
    }
}
