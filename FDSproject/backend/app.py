"""
Flask Server for Route Finder with Multiple Algorithms (Dijkstra, Bellman-Ford, Floyd-Warshall)
Handles API requests from frontend and integrates with Google Maps API
Includes Java-based algorithm implementations for performance comparison
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dijkstra import Graph, Dijkstra
from typing import Tuple, List, Optional
import math
import hashlib
from java_executor import get_executor
from collections import OrderedDict

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

GOOGLE_MAPS_API_KEY = "AIzaSyAbukOMoh-_w7xKb0q1VNvavXFK2WLR28E"

# In-memory graph storage (in production, use database)
location_graph = Graph()
custom_edges = []  # Persist user-defined edges across rebuilds
location_coords = {}  # Store coordinates for locations to avoid repeated geocoding
auto_graph_metric = "time"  # "time" (minutes) or "distance" (km) for all_pairs builds

# Location hashtable storage (like Java's Hashtable for persistent storage)
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
    
    def get(self, name):
        return self.locations.get(name.lower())
    
    def has(self, name):
        return name.lower() in self.locations
    
    def remove(self, name):
        return self.locations.pop(name.lower(), None)
    
    def getAll(self):
        return list(self.locations.values())
    
    def clear(self):
        self.locations.clear()
    
    def count(self):
        return len(self.locations)

location_hashtable = LocationHashtable()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (fallback when Distance Matrix is unavailable)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def estimate_drive_minutes_from_km(km: float, kph: float = 40.0) -> float:
    """Rough urban drive time from straight-line distance (fallback)."""
    if kph <= 0:
        kph = 40.0
    return (km / kph) * 60.0


NOMINATIM_USER_AGENT = "DijkstraRouteFinder/1.0 (educational project; OSM Nominatim usage policy)"


def fallback_coordinates_near_pune(location_name: str) -> Tuple[float, float]:
    """
    Last-resort pseudo-coordinates near Pune when no geocoder returns a result.
    Not the real address — only keeps the app usable offline.
    """
    pune_lat, pune_lng = 18.5204, 73.8567
    digest = hashlib.sha256(location_name.strip().lower().encode("utf-8")).hexdigest()
    dx = (int(digest[:6], 16) / 0xFFFFFF - 0.5) * 0.12
    dy = (int(digest[6:12], 16) / 0xFFFFFF - 0.5) * 0.12
    return pune_lat + dx, pune_lng + dy


def geocode_nominatim(location_name: str) -> Optional[Tuple[float, float, str]]:
    """
    OpenStreetMap Nominatim (free). Used when Google Geocoding fails so pins match
    the place name instead of a random hash near Pune.
    Returns (lat, lng, display_name) or None.
    """
    q = f"{location_name}, Pune, Maharashtra, India"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": q,
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }
    headers = {"User-Agent": NOMINATIM_USER_AGENT}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        response.raise_for_status()
        rows = response.json()
        if not rows:
            return None
        hit = rows[0]
        lat = float(hit["lat"])
        lng = float(hit["lon"])
        label = str(hit.get("display_name", q))[:200]
        return lat, lng, label
    except Exception as e:
        print(f"Nominatim geocode failed for {location_name!r}: {e}")
        return None


def resolve_coordinates(location_name: str) -> Tuple[float, float, str, Optional[str]]:
    """
    Resolve (lat, lng, source, matched_label).
    source is 'google' | 'nominatim' | 'approximate'.
    matched_label is a human-readable place name when available (Nominatim/Google).
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{location_name}, Pune, Maharashtra, India",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            formatted = data["results"][0].get("formatted_address")
            return float(loc["lat"]), float(loc["lng"]), "google", formatted
        print(f"Google Geocode status {data.get('status')!r} for {location_name!r}; trying Nominatim.")
    except Exception as e:
        print(f"Google Geocode error for {location_name!r}: {e}")

    nom = geocode_nominatim(location_name)
    if nom is not None:
        lat, lng, label = nom
        return lat, lng, "nominatim", label

    lat, lng = fallback_coordinates_near_pune(location_name)
    print(f"Using approximate coordinates for {location_name!r} (no geocoder hit).")
    return lat, lng, "approximate", None


def get_coordinates(location_name: str) -> Tuple[float, float]:
    """Backward-compatible: (lat, lng) only."""
    lat, lng, _src, _label = resolve_coordinates(location_name)
    return lat, lng


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
        km = haversine_km(origin[0], origin[1], destination[0], destination[1])
        return estimate_drive_minutes_from_km(km)
    except Exception as e:
        print(f"Error fetching driving time: {e}")
        km = haversine_km(origin[0], origin[1], destination[0], destination[1])
        return estimate_drive_minutes_from_km(km)


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
        return haversine_km(origin[0], origin[1], destination[0], destination[1])
    except Exception as e:
        print(f"Error fetching driving distance: {e}")
        return haversine_km(origin[0], origin[1], destination[0], destination[1])


def fetch_osrm_duration_matrix(lat_lng_list: List[Tuple[float, float]]) -> Optional[List[List[Optional[float]]]]:
    """
    OSRM Table API: driving duration in seconds between each ordered pair (asymmetric).
    Uses real road network distances so Dijkstra does not prefer bogus 'shortcuts'
    from straight-line / rough estimates (e.g. unwanted detours through extra areas).
    """
    if len(lat_lng_list) < 2:
        return None
    coord_str = ";".join(f"{lng},{lat}" for lat, lng in lat_lng_list)
    url = f"https://router.project-osrm.org/table/v1/driving/{coord_str}"
    try:
        response = requests.get(
            url,
            params={"annotations": "duration"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "Ok" or not data.get("durations"):
            return None
        return data["durations"]
    except Exception as e:
        print(f"OSRM duration matrix failed: {e}")
        return None


def fetch_osrm_distance_matrix(lat_lng_list: List[Tuple[float, float]]) -> Optional[List[List[Optional[float]]]]:
    """
    OSRM Table API: driving distance in meters between each ordered pair (asymmetric).
    Suitable for true shortest-distance routing (weight = meters/km), independent of speed.
    """
    if len(lat_lng_list) < 2:
        return None
    coord_str = ";".join(f"{lng},{lat}" for lat, lng in lat_lng_list)
    url = f"https://router.project-osrm.org/table/v1/driving/{coord_str}"
    try:
        response = requests.get(
            url,
            params={"annotations": "distance"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "Ok" or not data.get("distances"):
            return None
        return data["distances"]
    except Exception as e:
        print(f"OSRM distance matrix failed: {e}")
        return None


def fetch_road_geometry_osrm(lat_lng_pairs: List[Tuple[float, float]]) -> Optional[List[List[float]]]:
    """
    Driving polyline through waypoints in order (OpenStreetMap via public OSRM).
    lat_lng_pairs: (lat, lng) per Dijkstra waypoint. Returns [[lat, lng], ...] for Leaflet.
    """
    if len(lat_lng_pairs) < 2:
        return None
    coord_str = ";".join(f"{lng},{lat}" for lat, lng in lat_lng_pairs)
    url = f"https://router.project-osrm.org/route/v1/driving/{coord_str}"
    try:
        response = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        coords = data["routes"][0]["geometry"]["coordinates"]
        return [[pt[1], pt[0]] for pt in coords]
    except Exception as e:
        print(f"OSRM road geometry failed: {e}")
        return None


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({"status": "Dijkstra Route Finder API is running"})


@app.route('/api/reset', methods=['POST'])
def reset_state():
    """Clear graph, cached coordinates, and custom edges (keeps in sync with frontend Clear All)."""
    location_graph.graph.clear()
    location_graph.vertices.clear()
    custom_edges.clear()
    location_coords.clear()
    location_hashtable.clear()
    return jsonify({"message": "Server state cleared"})


@app.route('/api/locations', methods=['POST'])
def add_location():
    """
    Add a location to the system
    Expected JSON: {"name": "location_name"}
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
    location_name = str(data.get("name", "")).strip()
    
    if not location_name:
        return jsonify({"error": "Location name is required"}), 400
    
    lat, lng, geocode_source, matched_label = resolve_coordinates(location_name)

    location_coords[location_name] = (lat, lng)
    location_graph.vertices.add(location_name)
    
    # Store in hashtable for retrieval later
    location_hashtable.add(location_name, lat, lng, geocode_source, matched_label)

    payload = {
        "name": location_name,
        "coordinates": {"lat": lat, "lng": lng},
        "geocode_source": geocode_source,
        "message": "Location added successfully",
    }
    if matched_label:
        payload["matched_place"] = matched_label
    if geocode_source == "approximate":
        payload["warning"] = (
            "Could not find this name on the map; pin is approximate near Pune. "
            "Try a clearer name (e.g. area + Pune) or check your network."
        )
    return jsonify(payload)

    payload = {
        "name": location_name,
        "coordinates": {"lat": lat, "lng": lng},
        "geocode_source": geocode_source,
        "message": "Location added successfully",
    }
    if matched_label:
        payload["matched_place"] = matched_label
    if geocode_source == "approximate":
        payload["warning"] = (
            "Could not find this name on the map; pin is approximate near Pune. "
            "Try a clearer name (e.g. area + Pune) or check your network."
        )
    return jsonify(payload)


@app.route('/api/locations/build-graph', methods=['POST'])
def build_graph():
    """
    Build graph from list of locations
    Expected JSON: {"locations": ["loc1", "loc2", ...], "mode": "custom_edges_only"|"all_pairs"}
    If mode==custom_edges_only (default), only vertices are registered and custom edges are reapplied.
    If mode==all_pairs, pairwise edges are created using driving time (minutes).
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
    global auto_graph_metric
    locations = data.get("locations", [])
    mode = str(data.get("mode", "custom_edges_only")).strip()
    metric = str(data.get("metric", "time")).strip().lower()
    if metric not in ("time", "distance"):
        return jsonify({"error": "metric must be 'time' or 'distance'"}), 400
    
    if len(locations) < 2:
        return jsonify({"error": "At least 2 locations are required"}), 400
    
    # Clear existing graph but keep custom edges list intact
    location_graph.graph.clear()
    location_graph.vertices.clear()
    
    # Get coordinates for all locations
    graph_coords = {}
    for location in locations:
        if location in graph_coords:
            coords = graph_coords[location]
        elif location in location_coords:
            coords = location_coords[location]
        else:
            lat, lng = get_coordinates(location)
            coords = (lat, lng)
            location_coords[location] = coords
        graph_coords[location] = coords
        location_graph.vertices.add(location)
    
    # Optionally build complete directed graph using OSRM (real roads)
    edges_added = 0
    if mode == "all_pairs":
        auto_graph_metric = metric
        coords_list = [location_coords[loc] for loc in locations]
        matrix = fetch_osrm_distance_matrix(coords_list) if metric == "distance" else fetch_osrm_duration_matrix(coords_list)
        n = len(locations)
        if matrix and len(matrix) >= n:
            for i in range(n):
                row = matrix[i] if i < len(matrix) else []
                for j in range(n):
                    if i == j:
                        continue
                    loc_i = locations[i]
                    loc_j = locations[j]
                    sec = None
                    if j < len(row):
                        sec = row[j]
                    if metric == "distance":
                        # OSRM returns meters; store weight as kilometers for readability
                        if sec is not None and sec > 0:
                            w = float(sec) / 1000.0
                        else:
                            w = get_driving_distance(location_coords[loc_i], location_coords[loc_j])
                    else:
                        # OSRM returns seconds; store weight as minutes
                        if sec is not None and sec > 0:
                            w = float(sec) / 60.0
                        else:
                            w = get_driving_time(location_coords[loc_i], location_coords[loc_j])
                    location_graph.add_edge(loc_i, loc_j, float(w))
                    edges_added += 1
            print(f"Build graph: used OSRM {metric} matrix for {n} locations ({edges_added} directed edges).")
        else:
            for i, loc1 in enumerate(locations):
                for j, loc2 in enumerate(locations):
                    if i < j:
                        if metric == "distance":
                            w = get_driving_distance(location_coords[loc1], location_coords[loc2])
                        else:
                            w = get_driving_time(location_coords[loc1], location_coords[loc2])
                        location_graph.add_bidirectional_edge(loc1, loc2, float(w))
                        edges_added += 2
            print("Build graph: OSRM matrix unavailable; used fallback edge weights.")
    
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
        "mode": mode,
        "metric": metric
    })


def _route_json_response(path: List[str], total_time: float, constraint: str, via_chain: Optional[List[str]] = None):
    """Shared response builder for /api/route (path is ordered vertex names)."""
    path_coords = []
    for location in path:
        coords = location_coords.get(location)
        if coords:
            lat, lng = coords
        else:
            lat, lng = get_coordinates(location)
            if lat is not None and lng is not None:
                location_coords[location] = (lat, lng)
        if lat is not None and lng is not None:
            path_coords.append({
                "name": location,
                "coordinates": {"lat": lat, "lng": lng}
            })

    total_sec = int(round(float(total_time) * 60))
    mins, secs = divmod(total_sec, 60)

    lat_lng_order: List[Tuple[float, float]] = [
        (entry["coordinates"]["lat"], entry["coordinates"]["lng"])
        for entry in path_coords
        if entry.get("coordinates")
    ]
    road_geometry = fetch_road_geometry_osrm(lat_lng_order) if len(lat_lng_order) >= 2 else None

    unit = "km" if auto_graph_metric == "distance" else "min"
    out = {
        "path": path,
        "algorithm": "Dijkstra",
        "constraint": constraint,
        "total_time_minutes": round(total_time, 2),
        "total_time_formatted": f"{mins} min {secs} sec",
        "weight_unit": unit,
        "path_coordinates": path_coords,
        "waypoints": len(path),
        "road_geometry": road_geometry,
        "road_geometry_source": "OSRM" if road_geometry else None,
    }
    if via_chain:
        out["via_chain"] = via_chain
    return jsonify(out)


@app.route('/api/route', methods=['POST'])
def find_route():
    """
    Find shortest route using Dijkstra's algorithm.
    JSON: {"start", "end", "via": optional ["Baner", ...]}
    If via is set, shortest paths are chained: start→via1→…→end (road-realistic edge weights recommended).
    If via is omitted, a route must use at least one other vertex (direct start–end edge ignored).
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
    start = str(data.get("start", "")).strip()
    end = str(data.get("end", "")).strip()
    raw_via = data.get("via")

    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400

    if start not in location_graph.vertices:
        return jsonify({"error": f"Start location '{start}' not found in graph"}), 404

    if end not in location_graph.vertices:
        return jsonify({"error": f"End location '{end}' not found in graph"}), 404

    via_list: List[str] = []
    if raw_via is None:
        pass
    elif isinstance(raw_via, str):
        s = raw_via.strip()
        if s:
            via_list = [s]
    elif isinstance(raw_via, list):
        via_list = [str(v).strip() for v in raw_via if str(v).strip()]
    else:
        return jsonify({"error": "via must be a list of place names, a single string, or omitted"}), 400

    if via_list:
        chain = [start] + via_list + [end]
        if len(set(chain)) != len(chain):
            return jsonify({"error": "Start, Via stops, and End must all be different locations."}), 400
        for name in chain:
            if name not in location_graph.vertices:
                return jsonify({"error": f"Location '{name}' is not in the graph"}), 404

        dijkstra = Dijkstra(location_graph)
        merged_path: List[str] = []
        total_time = 0.0
        for k in range(len(chain) - 1):
            a, b = chain[k], chain[k + 1]
            seg_path, seg_w = dijkstra.find_shortest_path(a, b)
            if seg_path is None:
                return jsonify({"error": f"No path found from '{a}' to '{b}'. Rebuild the graph or add edges."}), 404
            total_time += float(seg_w)
            if k == 0:
                merged_path.extend(seg_path)
            else:
                merged_path.extend(seg_path[1:])

        return _route_json_response(merged_path, total_time, "via_waypoints", via_chain=chain)

    other_vertices = location_graph.vertices - {start, end}
    if len(other_vertices) < 1:
        return jsonify({
            "error": (
                "Add at least one more location, or set Via to force a path through a specific place. "
                "Routes without Via must pass through at least one intermediate stop."
            )
        }), 400

    routed_graph = location_graph.copy_excluding_direct_connection(start, end)
    dijkstra = Dijkstra(routed_graph)
    path, total_time = dijkstra.find_shortest_path(start, end)

    if path is None:
        has_edge = any(
            bool(location_graph.get_neighbors(v)) for v in location_graph.vertices
        )
        if not has_edge:
            return jsonify({
                "error": (
                    "No edges in the graph. Add edges between locations, or click "
                    "'Build Graph (Auto-connect all locations)'."
                )
            }), 404
        return jsonify({
            "error": (
                "No route from start to end that uses at least one other location. "
                "Try setting Via (e.g. Baner), or add connections so an indirect path exists."
            )
        }), 404

    if len(path) < 3:
        return jsonify({
            "error": (
                "Could not produce a path with at least one node between start and end. "
                "Add more connections or use Via to choose a corridor."
            )
        }), 404

    return _route_json_response(path, float(total_time), "at_least_one_intermediate_vertex")


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
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
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
        # Auto-compute using stored coordinates or Google
        u_latlng = location_coords.get(u) or get_coordinates(u)
        v_latlng = location_coords.get(v) or get_coordinates(v)
        if u_latlng is None or v_latlng is None or u_latlng[0] is None or v_latlng[0] is None:
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


@app.route('/api/locations/all', methods=['GET'])
def get_all_locations():
    """Retrieve all stored locations from hashtable"""
    locations = location_hashtable.getAll()
    return jsonify({
        "count": location_hashtable.count(),
        "locations": locations
    })


@app.route('/api/locations/<name>', methods=['GET'])
def get_location(name):
    """Retrieve a specific location from hashtable by name"""
    loc = location_hashtable.get(name)
    if not loc:
        return jsonify({"error": f"Location '{name}' not found in hashtable"}), 404
    return jsonify(loc)


@app.route('/api/algorithms/compare', methods=['POST'])
def compare_algorithms():
    """
    Compare all three algorithms (Dijkstra, Bellman-Ford, Floyd-Warshall)
    JSON: {"start": "location1", "end": "location2"}
    Returns: execution times and results for all three algorithms
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
    
    start = str(data.get("start", "")).strip()
    end = str(data.get("end", "")).strip()
    
    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400
    
    if start not in location_graph.vertices:
        return jsonify({"error": f"Start location '{start}' not found in graph"}), 404
    
    if end not in location_graph.vertices:
        return jsonify({"error": f"End location '{end}' not found in graph"}), 404
    
    # Prepare data for Java algorithms
    vertices = list(location_graph.vertices)
    edges = []
    
    for u in location_graph.graph:
        for v, weight in location_graph.get_neighbors(u):
            edges.append({
                "from": u,
                "to": v,
                "weight": weight
            })
    
    if not edges:
        return jsonify({"error": "Graph has no edges. Build the graph first."}), 400
    
    # Run Java algorithms
    executor = get_executor()
    results = executor.run_algorithms(vertices, edges, start, end)
    
    if "error" in results:
        return jsonify({"error": f"Algorithm execution failed: {results['error']}"}), 500
    
    # Parse results and create comparison
    comparison = {
        "start": start,
        "end": end,
        "algorithms": {}
    }
    
    # Process Dijkstra results
    if "dijkstra" in results:
        dij = results["dijkstra"]
        comparison["algorithms"]["dijkstra"] = {
            "name": "Dijkstra",
            "distance": dij.get("distance", 0),
            "path": dij.get("path", []),
            "execution_time_ms": dij.get("execution_time_ms", 0),
            "complexity": dij.get("complexity", "O((V + E) log V)"),
            "steps_count": len(dij.get("steps", []))
        }
    
    # Process Bellman-Ford results
    if "bellman_ford" in results:
        bf = results["bellman_ford"]
        comparison["algorithms"]["bellman_ford"] = {
            "name": "Bellman-Ford",
            "distance": bf.get("distance", 0),
            "path": bf.get("path", []),
            "execution_time_ms": bf.get("execution_time_ms", 0),
            "complexity": bf.get("complexity", "O(V * E)"),
            "steps_count": len(bf.get("steps", [])),
            "has_negative_cycle": bf.get("has_negative_cycle", False)
        }
    
    # Process Floyd-Warshall results
    if "floyd_warshall" in results:
        fw = results["floyd_warshall"]
        comparison["algorithms"]["floyd_warshall"] = {
            "name": "Floyd-Warshall",
            "distance": fw.get("distance", 0),
            "path": fw.get("path", []),
            "execution_time_ms": fw.get("execution_time_ms", 0),
            "complexity": fw.get("complexity", "O(V³)"),
            "steps_count": fw.get("step_count", len(fw.get("steps", [])))
        }
    
    # Calculate performance metrics
    times = [comparison["algorithms"][algo]["execution_time_ms"] 
             for algo in comparison["algorithms"]]
    if times:
        fastest = min(times)
        slowest = max(times)
        comparison["performance_summary"] = {
            "fastest_algorithm": [algo for algo, data in comparison["algorithms"].items() 
                                 if data["execution_time_ms"] == fastest][0],
            "slowest_algorithm": [algo for algo, data in comparison["algorithms"].items() 
                                 if data["execution_time_ms"] == slowest][0],
            "time_difference_ms": slowest - fastest
        }
    
    return jsonify(comparison)


@app.route('/api/algorithms/dijkstra', methods=['POST'])
def find_route_dijkstra():
    """Find shortest route using only Dijkstra (Python implementation)"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400
    start = str(data.get("start", "")).strip()
    end = str(data.get("end", "")).strip()
    
    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400
    
    if start not in location_graph.vertices:
        return jsonify({"error": f"Start location '{start}' not found in graph"}), 404
    
    if end not in location_graph.vertices:
        return jsonify({"error": f"End location '{end}' not found in graph"}), 404
    
    dijkstra = Dijkstra(location_graph)
    path, total_time = dijkstra.find_shortest_path(start, end)
    
    if path is None:
        return jsonify({"error": "No path found between these locations"}), 404
    
    return _route_json_response(path, float(total_time), "dijkstra_only")


if __name__ == '__main__':
    print("Starting Route Finder Server with Multiple Algorithms...")
    print(f"Google Maps API Key: {GOOGLE_MAPS_API_KEY[:20]}...")
    print("Initializing Java algorithm executor...")
    executor = get_executor()
    app.run(debug=True, port=5000)

