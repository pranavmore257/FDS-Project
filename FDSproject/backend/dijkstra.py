"""
Dijkstra's Algorithm Implementation for Shortest Path Finding
Uses appropriate data structures: Priority Queue (Heap) and Graph (Adjacency List)
"""

import heapq
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class Graph:
    """
    Graph class using adjacency list representation
    Efficient for sparse graphs
    """
    
    def __init__(self):
        self.graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.vertices: set = set()
    
    def add_edge(self, from_vertex: str, to_vertex: str, weight: float):
        """
        Add a directed edge to the graph
        weight represents time in minutes
        """
        self.graph[from_vertex].append((to_vertex, weight))
        self.vertices.add(from_vertex)
        self.vertices.add(to_vertex)
    
    def add_bidirectional_edge(self, from_vertex: str, to_vertex: str, weight: float):
        """Add bidirectional edge (both directions)"""
        self.add_edge(from_vertex, to_vertex, weight)
        self.add_edge(to_vertex, from_vertex, weight)
    
    def get_neighbors(self, vertex: str) -> List[Tuple[str, float]]:
        """Get all neighbors of a vertex"""
        return self.graph.get(vertex, [])
    
    def get_all_vertices(self) -> set:
        """Get all vertices in the graph"""
        return self.vertices


class Dijkstra:
    """
    Dijkstra's Algorithm implementation using Priority Queue (Min Heap)
    Time Complexity: O((V + E) log V) where V is vertices, E is edges
    Space Complexity: O(V)
    """
    
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[Optional[List[str]], Optional[float]]:
        """
        Find shortest path from start to end using Dijkstra's algorithm
        
        Returns:
            Tuple of (path as list of vertices, total_time) or (None, None) if no path exists
        """
        if start not in self.graph.vertices or end not in self.graph.vertices:
            return None, None
        
        # Priority Queue (Min Heap): (distance, vertex)
        # Using tuple (distance, vertex) for automatic min-heap behavior
        priority_queue: List[Tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))
        
        # Distance dictionary: vertex -> shortest distance from start
        distances: Dict[str, float] = {v: float('inf') for v in self.graph.vertices}
        distances[start] = 0
        
        # Previous vertex dictionary for path reconstruction
        previous: Dict[str, Optional[str]] = {v: None for v in self.graph.vertices}
        
        # Visited set to track processed vertices
        visited: set = set()
        
        while priority_queue:
            # Extract vertex with minimum distance
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            # Skip if already visited with a shorter path
            if current_vertex in visited:
                continue
            
            # Mark as visited
            visited.add(current_vertex)
            
            # If we reached the destination, reconstruct path
            if current_vertex == end:
                path = self._reconstruct_path(previous, start, end)
                return path, distances[end]
            
            # Explore neighbors
            for neighbor, edge_weight in self.graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    continue
                
                # Calculate new distance
                new_distance = current_distance + edge_weight
                
                # If found shorter path, update
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # No path found
        return None, None
    
    def _reconstruct_path(self, previous: Dict[str, Optional[str]], start: str, end: str) -> List[str]:
        """Reconstruct path from previous dictionary"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path
    
    def find_all_shortest_distances(self, start: str) -> Dict[str, float]:
        """
        Find shortest distances from start to all other vertices
        Useful for finding multiple destinations
        """
        if start not in self.graph.vertices:
            return {}
        
        # Priority Queue
        priority_queue: List[Tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))
        
        # Distance dictionary
        distances: Dict[str, float] = {v: float('inf') for v in self.graph.vertices}
        distances[start] = 0
        
        # Visited set
        visited: set = set()
        
        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            if current_vertex in visited:
                continue
            
            visited.add(current_vertex)
            
            # Explore neighbors
            for neighbor, edge_weight in self.graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    continue
                
                new_distance = current_distance + edge_weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        return distances


