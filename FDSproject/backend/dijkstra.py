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

    def copy_excluding_direct_connection(self, a: str, b: str) -> "Graph":
        """
        Deep copy of the graph with all directed edges between a and b removed
        (both a→b and b→a). Used to force a route with at least one other vertex
        between start and end when a direct edge exists.
        """
        new_g = Graph()
        for u, nbrs in self.graph.items():
            for v, w in nbrs:
                if (u == a and v == b) or (u == b and v == a):
                    continue
                new_g.add_edge(u, v, w)
        new_g.vertices = set(self.vertices)
        return new_g


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
        for u in list(self.graph.graph.keys()):
            self.graph.vertices.add(u)
            for v, _ in self.graph.graph[u]:
                self.graph.vertices.add(v)

        if start not in self.graph.vertices or end not in self.graph.vertices:
            return None, None
        
       
        priority_queue: List[Tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))
        
        
        distances: Dict[str, float] = {v: float('inf') for v in self.graph.vertices}
        distances[start] = 0
        
        
        previous: Dict[str, Optional[str]] = {v: None for v in self.graph.vertices}
        
        
        visited: set = set()
        
        while priority_queue:
            
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            
            if current_vertex in visited:
                continue
            
           
            visited.add(current_vertex)
            
            
            if current_vertex == end:
                path = self._reconstruct_path(previous, start, end)
                return path, distances[end]
            
            
            for neighbor, edge_weight in self.graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    continue

                if neighbor not in distances:
                    distances[neighbor] = float('inf')
                    previous[neighbor] = None

                new_distance = current_distance + edge_weight
                
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        
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
        for u in list(self.graph.graph.keys()):
            self.graph.vertices.add(u)
            for v, _ in self.graph.graph[u]:
                self.graph.vertices.add(v)

        if start not in self.graph.vertices:
            return {}
        
        
        priority_queue: List[Tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))
        
        
        distances: Dict[str, float] = {v: float('inf') for v in self.graph.vertices}
        distances[start] = 0
        
        
        visited: set = set()
        
        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            if current_vertex in visited:
                continue
            
            visited.add(current_vertex)
            
            
            for neighbor, edge_weight in self.graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    continue

                if neighbor not in distances:
                    distances[neighbor] = float('inf')

                new_distance = current_distance + edge_weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        return distances


