import java.util.*;
import java.io.IOException;
import org.json.JSONObject;
import org.json.JSONArray;

/**
 * AlgorithmRunner: Main class to run all three shortest path algorithms
 * and compare their performance and results
 * Can be invoked from Python via command line with JSON input
 */
public class AlgorithmRunner {
    
    public static void main(String[] args) {
        try {
            if (args.length == 0) {
                System.err.println("Usage: java AlgorithmRunner <json_input>");
                System.exit(1);
            }
            
            String jsonInput = args[0];
            JSONObject input = new JSONObject(jsonInput);
            
            // Parse input
            JSONArray verticesArray = input.getJSONArray("vertices");
            JSONArray edgesArray = input.getJSONArray("edges");
            String source = input.getString("source");
            String destination = input.getString("destination");
            
            // Build graph
            Graph graph = new Graph(false); // undirected graph
            
            for (int i = 0; i < verticesArray.length(); i++) {
                String vertex = verticesArray.getString(i);
                graph.getVertices().add(vertex);
            }
            
            for (int i = 0; i < edgesArray.length(); i++) {
                JSONObject edge = edgesArray.getJSONObject(i);
                String from = edge.getString("from");
                String to = edge.getString("to");
                double weight = edge.getDouble("weight");
                graph.addEdge(from, to, weight);
            }
            
            // Run all three algorithms
            JSONObject results = new JSONObject();
            
            // Run Dijkstra
            DijkstraAlgorithm dijkstra = new DijkstraAlgorithm(graph);
            DijkstraAlgorithm.DijkstraResult dijkstraResult = 
                dijkstra.findShortestPath(source, destination);
            results.put("dijkstra", formatDijkstraResult(dijkstraResult, dijkstra.getSteps()));
            
            // Run Bellman-Ford
            BellmanFordAlgorithm bellmanFord = new BellmanFordAlgorithm(graph);
            BellmanFordAlgorithm.BellmanFordResult bellmanFordResult = 
                bellmanFord.findShortestPath(source, destination);
            results.put("bellman_ford", formatBellmanFordResult(bellmanFordResult, bellmanFord.getSteps()));
            
            // Run Floyd-Warshall
            FloydWarshallAlgorithm floydWarshall = new FloydWarshallAlgorithm(graph);
            FloydWarshallAlgorithm.FloydWarshallResult floydWarshallResult = 
                floydWarshall.findShortestPath(source, destination);
            results.put("floyd_warshall", formatFloydWarshallResult(floydWarshallResult, floydWarshall.getSteps()));
            
            // Output as JSON
            System.out.println(results.toString());
            
        } catch (Exception e) {
            JSONObject error = new JSONObject();
            error.put("error", e.getMessage());
            System.out.println(error.toString());
            System.exit(1);
        }
    }
    
    private static JSONObject formatDijkstraResult(
            DijkstraAlgorithm.DijkstraResult result,
            List<String> steps) {
        JSONObject obj = new JSONObject();
        obj.put("algorithm", "Dijkstra");
        obj.put("distance", result.totalDistance);
        obj.put("path", new JSONArray(result.path));
        obj.put("execution_time_ms", result.executionTimeMs);
        obj.put("steps", new JSONArray(steps));
        obj.put("complexity", "O((V + E) log V)");
        return obj;
    }
    
    private static JSONObject formatBellmanFordResult(
            BellmanFordAlgorithm.BellmanFordResult result,
            List<String> steps) {
        JSONObject obj = new JSONObject();
        obj.put("algorithm", "Bellman-Ford");
        obj.put("distance", result.totalDistance);
        obj.put("path", new JSONArray(result.path));
        obj.put("execution_time_ms", result.executionTimeMs);
        obj.put("steps", new JSONArray(steps));
        obj.put("complexity", "O(V * E)");
        obj.put("has_negative_cycle", result.hasNegativeCycle);
        if (result.hasNegativeCycle) {
            obj.put("error", result.errorMessage);
        }
        return obj;
    }
    
    private static JSONObject formatFloydWarshallResult(
            FloydWarshallAlgorithm.FloydWarshallResult result,
            List<String> steps) {
        JSONObject obj = new JSONObject();
        obj.put("algorithm", "Floyd-Warshall");
        obj.put("distance", result.totalDistance);
        obj.put("path", new JSONArray(result.path));
        obj.put("execution_time_ms", result.executionTimeMs);
        obj.put("steps", new JSONArray(steps.subList(0, Math.min(50, steps.size()))));
        obj.put("complexity", "O(V³)");
        obj.put("step_count", steps.size());
        return obj;
    }
}
