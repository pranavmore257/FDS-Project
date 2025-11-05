"""
Flask Server for Dijkstra Algorithm Route Finder
Handles API requests from frontend and integrates with Google Maps API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dijkstra import Graph, Dijkstra
from typing import Tuple
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

GOOGLE_MAPS_API_KEY = "AIzaSyAbukOMoh-_w7xKb0q1VNvavXFK2WLR28E"

# In-memory graph storage (in production, use database)
location_graph = Graph()
custom_edges = []  # Persist user-defined edges across rebuilds


def get_coordinates(location_name: str) -> Tuple[float, float]:
    """
    Get coordinates for a location using Google Geocoding API
    Returns: (latitude, longitude)
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{location_name}, Pune, Maharashtra, India",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None


def get_driving_time(origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
    """
    Get driving time between two coordinates using Google Distance Matrix API
    Returns: time in minutes
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin[0]},{origin[1]}",
        "destinations": f"{destination[0]},{destination[1]}",
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["status"] == "OK" and data["rows"]:
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                # Convert seconds to minutes
                time_in_seconds = element["duration"]["value"]
                return time_in_seconds / 60.0
        return None
    except Exception as e:
        print(f"Error fetching driving time: {e}")
        return None


def get_driving_distance(origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
    """
    Get driving distance between two coordinates using Google Distance Matrix API
    Returns: distance in kilometers
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin[0]},{origin[1]}",
        "destinations": f"{destination[0]},{destination[1]}",
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data["status"] == "OK" and data["rows"]:
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                # meters to kilometers
                distance_meters = element["distance"]["value"]
                return distance_meters / 1000.0
        return None
    except Exception as e:
        print(f"Error fetching driving distance: {e}")
        return None


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({"status": "Dijkstra Route Finder API is running"})


@app.route('/api/locations', methods=['POST'])
def add_location():
    """
    Add a location to the system
    Expected JSON: {"name": "location_name"}
    """
    data = request.get_json()
    location_name = data.get("name", "").strip()
    
    if not location_name:
        return jsonify({"error": "Location name is required"}), 400
    
    # Get coordinates for the location
    lat, lng = get_coordinates(location_name)
    
    if lat is None or lng is None:
        return jsonify({"error": f"Could not find coordinates for {location_name}"}), 404
    
    return jsonify({
        "name": location_name,
        "coordinates": {"lat": lat, "lng": lng},
        "message": "Location added successfully"
    })


@app.route('/api/locations/build-graph', methods=['POST'])
def build_graph():
    """
    Build graph from list of locations
    Expected JSON: {"locations": ["loc1", "loc2", ...], "mode": "custom_edges_only"|"all_pairs"}
    If mode==custom_edges_only (default), only vertices are registered and custom edges are reapplied.
    If mode==all_pairs, pairwise edges are created using driving time (minutes).
    """
    data = request.get_json()
    locations = data.get("locations", [])
    mode = str(data.get("mode", "custom_edges_only")).strip()
    
    if len(locations) < 2:
        return jsonify({"error": "At least 2 locations are required"}), 400
    
    # Clear existing graph but keep custom edges list intact
    location_graph.graph.clear()
    location_graph.vertices.clear()
    
    # Get coordinates for all locations
    location_coords = {}
    for location in locations:
        lat, lng = get_coordinates(location)
        if lat is None or lng is None:
            return jsonify({"error": f"Could not find coordinates for {location}"}), 404
        location_coords[location] = (lat, lng)
        location_graph.vertices.add(location)
    
    # Optionally build complete graph (all pairs) with time weights
    edges_added = 0
    if mode == "all_pairs":
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations):
                if i != j:
                    time = get_driving_time(location_coords[loc1], location_coords[loc2])
                    if time is not None:
                        location_graph.add_bidirectional_edge(loc1, loc2, time)
                        edges_added += 1
    
    # Re-apply custom user edges to the graph
    reapplied = 0
    for edge in custom_edges:
        u = edge.get("from")
        v = edge.get("to")
        w = edge.get("weight")
        bidir = edge.get("bidirectional", True)
        if u in location_graph.vertices and v in location_graph.vertices and isinstance(w, (int, float)):
            if bidir:
                location_graph.add_bidirectional_edge(u, v, float(w))
            else:
                location_graph.add_edge(u, v, float(w))
            reapplied += 1

    return jsonify({
        "message": "Graph built successfully",
        "vertices": len(locations),
        "edges": edges_added,
        "custom_edges_reapplied": reapplied,
        "locations": locations,
        "mode": mode
    })


@app.route('/api/route', methods=['POST'])
def find_route():
    """
    Find shortest route using Dijkstra's algorithm
    Expected JSON: {"start": "start_location", "end": "end_location"}
    """
    data = request.get_json()
    start = data.get("start", "").strip()
    end = data.get("end", "").strip()
    
    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400
    
    # Ensure locations exist in graph
    if start not in location_graph.vertices:
        return jsonify({"error": f"Start location '{start}' not found in graph"}), 404
    
    if end not in location_graph.vertices:
        return jsonify({"error": f"End location '{end}' not found in graph"}), 404
    
    # Find shortest path using Dijkstra
    dijkstra = Dijkstra(location_graph)
    path, total_time = dijkstra.find_shortest_path(start, end)
    
    if path is None:
        return jsonify({"error": "No path found between the locations"}), 404
    
    # Get coordinates for path visualization
    path_coords = []
    for location in path:
        lat, lng = get_coordinates(location)
        if lat and lng:
            path_coords.append({
                "name": location,
                "coordinates": {"lat": lat, "lng": lng}
            })
    
    return jsonify({
        "path": path,
        "total_time_minutes": round(total_time, 2),
        "total_time_formatted": f"{int(total_time)} min {int((total_time % 1) * 60)} sec",
        "path_coordinates": path_coords,
        "waypoints": len(path)
    })


@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get current graph structure"""
    graph_data = {
        "vertices": list(location_graph.vertices),
        "edges": {}
    }
    
    for vertex in location_graph.vertices:
        neighbors = location_graph.get_neighbors(vertex)
        graph_data["edges"][vertex] = [
            {"to": neighbor, "weight": weight} 
            for neighbor, weight in neighbors
        ]
    
    return jsonify(graph_data)


@app.route('/api/edges', methods=['POST'])
def add_edge():
    """Add a custom edge.
    JSON: {from, to, weight?, bidirectional?, metric?}
    If weight is omitted/null, it will be computed from Google based on metric:
      - metric == 'time' -> minutes (default for provided weights)
      - metric == 'distance' -> kilometers
    """
    data = request.get_json()
    u = str(data.get("from", "")).strip()
    v = str(data.get("to", "")).strip()
    weight = data.get("weight", None)
    bidirectional = bool(data.get("bidirectional", True))
    metric = str(data.get("metric", "distance")).strip().lower()

    if not u or not v:
        return jsonify({"error": "'from' and 'to' locations are required"}), 400
    if u == v:
        return jsonify({"error": "'from' and 'to' must be different"}), 400
    # Ensure vertices exist
    if u not in location_graph.vertices or v not in location_graph.vertices:
        return jsonify({"error": "Both locations must be added before creating an edge"}), 404

    # Resolve weight
    weight_val = None
    if weight is None or str(weight).strip() == "":
        # Auto-compute using Google
        u_latlng = get_coordinates(u)
        v_latlng = get_coordinates(v)
        if not u_latlng or not v_latlng or u_latlng[0] is None or v_latlng[0] is None:
            return jsonify({"error": "Could not resolve coordinates for one or both locations"}), 400
        if metric == "time":
            weight_val = get_driving_time(u_latlng, v_latlng)
            if weight_val is None:
                return jsonify({"error": "Failed to compute driving time from map"}), 502
        else:
            # default to distance
            weight_val = get_driving_distance(u_latlng, v_latlng)
            if weight_val is None:
                return jsonify({"error": "Failed to compute driving distance from map"}), 502
    else:
        try:
            weight_val = float(weight)
            if weight_val <= 0:
                return jsonify({"error": "'weight' must be positive"}), 400
        except Exception:
            return jsonify({"error": "'weight' must be a number"}), 400

    # Add to graph
    if bidirectional:
        location_graph.add_bidirectional_edge(u, v, weight_val)
    else:
        location_graph.add_edge(u, v, weight_val)

    # Persist edge for future rebuilds
    custom_edges.append({
        "from": u,
        "to": v,
        "weight": weight_val,
        "bidirectional": bidirectional,
        "metric": metric
    })

    return jsonify({
        "message": "Edge added successfully",
        "edge": {"from": u, "to": v, "weight": weight_val, "bidirectional": bidirectional, "metric": metric}
    })


if __name__ == '__main__':
    print("Starting Dijkstra Route Finder Server...")
    print(f"Google Maps API Key: {GOOGLE_MAPS_API_KEY[:20]}...")
    app.run(debug=True, port=5000)

