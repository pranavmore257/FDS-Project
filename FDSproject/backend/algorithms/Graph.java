import java.util.*;

/**
 * Graph class using adjacency list representation
 * Efficient for sparse graphs and supports all three algorithms
 */
public class Graph {
    private Map<String, List<Edge>> adjacencyList;
    private Set<String> vertices;
    private Map<String, Map<String, Double>> adjMatrix; // For Floyd-Warshall
    private boolean isDirected;
    
    public static class Edge {
        public String to;
        public double weight;
        
        public Edge(String to, double weight) {
            this.to = to;
            this.weight = weight;
        }
    }
    
    public Graph(boolean isDirected) {
        this.adjacencyList = new HashMap<>();
        this.vertices = new HashSet<>();
        this.adjMatrix = new HashMap<>();
        this.isDirected = isDirected;
    }
    
    public void addEdge(String from, String to, double weight) {
        // Add to adjacency list
        adjacencyList.putIfAbsent(from, new ArrayList<>());
        adjacencyList.get(from).add(new Edge(to, weight));
        
        vertices.add(from);
        vertices.add(to);
        
        // Add to adjacency matrix for Floyd-Warshall
        adjMatrix.putIfAbsent(from, new HashMap<>());
        adjMatrix.get(from).put(to, weight);
        
        if (!isDirected) {
            adjacencyList.putIfAbsent(to, new ArrayList<>());
            adjacencyList.get(to).add(new Edge(from, weight));
            adjMatrix.putIfAbsent(to, new HashMap<>());
            adjMatrix.get(to).put(from, weight);
        }
    }
    
    public List<Edge> getNeighbors(String vertex) {
        return adjacencyList.getOrDefault(vertex, new ArrayList<>());
    }
    
    public Set<String> getVertices() {
        return vertices;
    }
    
    public Map<String, List<Edge>> getAdjacencyList() {
        return adjacencyList;
    }
    
    public Map<String, Map<String, Double>> getAdjMatrix() {
        return adjMatrix;
    }
}
