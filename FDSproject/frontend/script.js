// Global variables
let map;
let markers = [];
let locations = [];
let edges = [];
let edgeMarkers = [];
let routeLayer = null;

const API_BASE = 'http://127.0.0.1:5000';

function escapeHtml(text) {
    if (text == null || text === '') return '';
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function readJsonSafe(response) {
    return response.text().then((text) => {
        try {
            return JSON.parse(text);
        } catch (e) {
            const snippet = text ? text.slice(0, 120).replace(/\s+/g, ' ') : '';
            throw new Error(
                snippet || 'Server did not return JSON. Start the backend: cd backend && python app.py'
            );
        }
    });
}

function apiFetch(url, options = {}) {
    return fetch(url, options).then(async (response) => {
        const data = await readJsonSafe(response);
        if (!response.ok) {
            const msg = data.error || data.message || `Request failed (${response.status})`;
            throw new Error(msg);
        }
        return data;
    });
}

// Initialize Leaflet map with OSM
function initMap() {
    map = L.map('map').setView([18.5204, 73.8567], 11);
    // Try CartoDB tiles first (more reliable), fallback to OSM
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors, © CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
    document.getElementById('mapLoading').style.display = 'none';
}

// Add location to the list
function addLocation() {
    const locationInput = document.getElementById('locationInput');
    const locationName = locationInput.value.trim();
    const loadingElement = document.getElementById('mapLoading');
    
    if (!locationName) {
        alert('Please enter a location name');
        return;
    }
    
    if (locations.some(loc => loc.name.toLowerCase() === locationName.toLowerCase())) {
        alert('This location already exists');
        return;
    }
    
    loadingElement.style.display = 'block';
    loadingElement.textContent = 'Searching location...';
    
    apiFetch(`${API_BASE}/api/locations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: locationName
        })
    })
    .then(data => {
        if (data.warning) {
            alert(data.warning);
        }

        const location = {
            name: locationName,
            lat: data.coordinates.lat,
            lng: data.coordinates.lng,
            geocodeSource: data.geocode_source,
            matchedPlace: data.matched_place || null
        };

        let popup = `<strong>${escapeHtml(locationName)}</strong>`;
        if (data.matched_place) {
            popup += `<br><small>${escapeHtml(data.matched_place)}</small>`;
        }
        if (data.geocode_source === 'nominatim') {
            popup += '<br><small style="opacity:0.85">Located with OpenStreetMap</small>';
        } else if (data.geocode_source === 'google') {
            popup += '<br><small style="opacity:0.85">Located with Google</small>';
        }

        locations.push(location);
        addMarkerToMap(location.name, [location.lat, location.lng], popup);
        updateLocationsList();
        updateSelectOptions();
        updateEdgeSelects();
        updateAlgorithmSelects();
        locationInput.value = '';
        
        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds().pad(0.2));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message || 'Error adding location. Is the backend running on port 5000?');
    })
    .finally(() => {
        loadingElement.style.display = 'none';
    });
}

// Edge management functions
function updateEdgeSelects() {
    const fromSelect = document.getElementById('edgeFrom');
    const toSelect = document.getElementById('edgeTo');
    
    // Store current selections
    const currentFrom = fromSelect.value;
    const currentTo = toSelect.value;
    
    // Clear existing options (keep the first empty option)
    fromSelect.innerHTML = '<option value="">From</option>';
    toSelect.innerHTML = '<option value="">To</option>';
    
    // Add current locations to both dropdowns
    locations.forEach(location => {
        const option1 = document.createElement('option');
        option1.value = location.name;
        option1.textContent = location.name;
        
        const option2 = option1.cloneNode(true);
        
        fromSelect.appendChild(option1);
        toSelect.appendChild(option2);
    });
    
    // Restore selections if they still exist
    if (currentFrom && locations.some(loc => loc.name === currentFrom)) {
        fromSelect.value = currentFrom;
    }
    if (currentTo && locations.some(loc => loc.name === currentTo)) {
        toSelect.value = currentTo;
    }
}

function addEdge() {
    const fromSelect = document.getElementById('edgeFrom');
    const toSelect = document.getElementById('edgeTo');
    const distanceInput = document.getElementById('edgeDistance');
    
    const from = fromSelect.value;
    const to = toSelect.value;
    const distanceValue = distanceInput.value.trim();
    const distance = distanceValue ? parseFloat(distanceValue) : null;
    
    // Validate inputs
    if (!from || !to) {
        alert('Please select both "From" and "To" locations');
        return;
    }
    
    if (from === to) {
        alert('"From" and "To" locations must be different');
        return;
    }
    
    // Validate distance if provided
    if (distanceValue && (isNaN(distance) || distance <= 0)) {
        alert('Please enter a valid distance greater than 0');
        distanceInput.focus();
        return;
    }
    
    // Check if edge already exists
    const edgeExists = edges.some(edge => 
        (edge.from === from && edge.to === to) || 
        (edge.from === to && edge.to === from)
    );
    
    if (edgeExists) {
        alert('A connection between these locations already exists');
        return;
    }
    
    // Prepare request data
    const requestData = {
        from: from,
        to: to
    };
    
    if (distance !== null) {
        // Use provided distance
        requestData.weight = distance;
        requestData.metric = 'distance';
    } else {
        // Auto-compute distance
        requestData.metric = 'distance';
    }
    
    apiFetch(`${API_BASE}/api/edges`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(data => {
        const actualDistance = data.edge.weight;
        const unit = data.edge.metric === 'time' ? 'min' : 'km';

        edges.push({ from, to, distance: actualDistance, unit });
        updateEdgesList();
        drawEdges();
        
        // Reset form
        fromSelect.value = '';
        toSelect.value = '';
        distanceInput.value = '';
        distanceInput.focus();
    })
    .catch(error => {
        console.error('Error adding edge:', error);
        alert(error.message || 'Error adding edge.');
    });
}

function updateEdgesList() {
    const edgesList = document.getElementById('edgesList');
    edgesList.innerHTML = '';
    
    edges.forEach((edge, index) => {
        const edgeItem = document.createElement('div');
        edgeItem.className = 'edge-item';
        const u = edge.unit || 'km';
        const w = typeof edge.distance === 'number' ? edge.distance.toFixed(2) : edge.distance;
        edgeItem.innerHTML = `
            <span>${edge.from} ↔ ${edge.to}: ${w} ${u}</span>
            <button onclick="removeEdge(${index})">×</button>
        `;
        edgesList.appendChild(edgeItem);
    });
}

function removeEdge(index) {
    if (index >= 0 && index < edges.length) {
        edges.splice(index, 1);
        updateEdgesList();
        drawEdges();
    }
}

function drawEdges() {
    // Remove existing edge markers
    edgeMarkers.forEach(marker => map.removeLayer(marker));
    edgeMarkers = [];
    
    // Draw new edges
    edges.forEach(edge => {
        const fromLoc = locations.find(loc => loc.name === edge.from);
        const toLoc = locations.find(loc => loc.name === edge.to);
        
        if (fromLoc && toLoc) {
            // Create a polyline for the edge
            const polyline = L.polyline(
                [[fromLoc.lat, fromLoc.lng], [toLoc.lat, toLoc.lng]],
                { 
                    color: '#3b82f6',
                    weight: 3,
                    dashArray: '5, 5'
                }
            ).addTo(map);
            
            // Add distance label in the middle of the edge
            const midPoint = L.latLng(
                (fromLoc.lat + toLoc.lat) / 2,
                (fromLoc.lng + toLoc.lng) / 2
            );
            
            const unit = edge.unit || 'km';
            const w = typeof edge.distance === 'number' ? edge.distance.toFixed(1) : edge.distance;
            const label = L.marker(midPoint, {
                icon: L.divIcon({
                    className: 'edge-label',
                    html: `${w} ${unit}`,
                    iconSize: [60, 20]
                }),
                interactive: false
            }).addTo(map);
            
            edgeMarkers.push(polyline, label);
        }
    });
}

// Helper functions
function addMarkerToMap(locationName, coordinates, popupHtml = null) {
    const marker = L.marker(coordinates, {
        draggable: true
    }).bindPopup(popupHtml || escapeHtml(locationName))
      .addTo(map);
    
    // Store reference to the marker
    marker.name = locationName;
    markers.push(marker);
    
    // Update location on marker drag
    marker.on('dragend', function(e) {
        const newLatLng = e.target.getLatLng();
        const location = locations.find(loc => loc.name === locationName);
        
        if (location) {
            location.lat = newLatLng.lat;
            location.lng = newLatLng.lng;
            // Redraw edges when a marker is moved
            drawEdges();
        }
    });
}

function removeLocation(locationName) {
    const index = locations.findIndex(loc => loc.name === locationName);
    if (index > -1) {
        // Remove any edges connected to this location
        edges = edges.filter(edge => 
            edge.from !== locationName && edge.to !== locationName
        );
        
        locations.splice(index, 1);
        removeMarkerFromMap(locationName);
        updateLocationsList();
        updateSelectOptions();
        updateEdgeSelects();
        updateAlgorithmSelects();
        updateEdgesList();
        drawEdges();
    }
}

function updateLocationsList() {
    const locationsList = document.getElementById('locationsList');
    locationsList.innerHTML = '';
    
    locations.forEach(location => {
        const locationItem = document.createElement('div');
        locationItem.className = 'location-item';
        locationItem.innerHTML = `
            <span>${location.name}</span>
            <button onclick="removeLocation('${location.name.replace(/'/g, "\\'")}')">×</button>
        `;
        locationsList.appendChild(locationItem);
    });
}

function updateSelectOptions() {
    const startSelect = document.getElementById('startSelect');
    const endSelect = document.getElementById('endSelect');
    const viaSelect = document.getElementById('viaSelect');

    const currentStart = startSelect.value;
    const currentEnd = endSelect.value;
    const currentVia = viaSelect.value;

    startSelect.innerHTML = '<option value="">Select Start Point</option>';
    endSelect.innerHTML = '<option value="">Select End Point</option>';
    viaSelect.innerHTML = '<option value="">Via (optional)</option>';

    locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.name;
        option.textContent = location.name;

        startSelect.appendChild(option);
        endSelect.appendChild(option.cloneNode(true));
        viaSelect.appendChild(option.cloneNode(true));
    });

    if (currentStart && locations.some(loc => loc.name === currentStart)) {
        startSelect.value = currentStart;
    }
    if (currentEnd && locations.some(loc => loc.name === currentEnd)) {
        endSelect.value = currentEnd;
    }
    if (currentVia && locations.some(loc => loc.name === currentVia)) {
        viaSelect.value = currentVia;
    }
}

function removeMarkerFromMap(locationName) {
    const markerIndex = markers.findIndex(m => m.name === locationName);
    if (markerIndex > -1) {
        map.removeLayer(markers[markerIndex]);
        markers.splice(markerIndex, 1);
    }
}

function buildGraph() {
    if (locations.length < 2) {
        alert('Please add at least 2 locations before building the graph');
        return;
    }
    
    // Show loading
    const loadingText = 'Building graph with automatic distances...';
    const edgesList = document.getElementById('edgesList');
    edgesList.innerHTML = `<div class="loading">${loadingText}</div>`;
    
    // Get location names
    const locationNames = locations.map(loc => loc.name);
    
    apiFetch(`${API_BASE}/api/locations/build-graph`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            locations: locationNames,
            mode: 'all_pairs',
            metric: 'distance'
        })
    })
    .then(data => {
        edges.length = 0;
        const metricLabel = data.metric === 'distance' ? 'road distance (km)' : 'road time (min)';
        alert(
            `Graph built using ${metricLabel} (OSRM when available). ` +
            `${data.edges} directed edges among ${data.vertices} locations.`
        );
        fetchGraphData();
    })
    .catch(error => {
        console.error('Error building graph:', error);
        alert(error.message || 'Error building graph.');
        updateEdgesList();
    });
}

function fetchGraphData() {
    apiFetch(`${API_BASE}/api/graph`)
    .then(data => {
        // Update local edges array with graph data
        edges.length = 0; // Clear existing
        
        // Convert graph edges to local format
        for (const fromVertex in data.edges) {
            for (const edge of data.edges[fromVertex]) {
                // Only add bidirectional edges once (avoid duplicates)
                const existingEdge = edges.find(e =>
                    e.from === fromVertex && e.to === edge.to
                );

                if (!existingEdge) {
                    edges.push({
                        from: fromVertex,
                        to: edge.to,
                        distance: edge.weight,
                        unit: 'min'
                    });
                }
            }
        }
        
        updateEdgesList();
        drawEdges();
    })
    .catch(error => {
        console.error('Error fetching graph data:', error);
        alert(error.message || 'Could not load graph from server.');
    });
}

function clearAll() {
    fetch(`${API_BASE}/api/reset`, { method: 'POST' }).catch(() => {});

    // Clear markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Clear locations
    locations = [];
    
    // Clear edges
    edges = [];
    edgeMarkers.forEach(marker => map.removeLayer(marker));
    edgeMarkers = [];
    
    // Clear route
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }
    
    // Reset UI
    document.getElementById('locationsList').innerHTML = '';
    document.getElementById('edgesList').innerHTML = '';
    document.getElementById('startSelect').innerHTML = '<option value="">Select Start Point</option>';
    document.getElementById('endSelect').innerHTML = '<option value="">Select End Point</option>';
    document.getElementById('viaSelect').innerHTML = '<option value="">Via (optional)</option>';
    document.getElementById('edgeFrom').innerHTML = '<option value="">From</option>';
    document.getElementById('edgeTo').innerHTML = '<option value="">To</option>';
    document.getElementById('edgeDistance').value = '';
    document.getElementById('locationInput').value = '';
    
    // Hide route result
    document.getElementById('routeResult').style.display = 'none';
    
    // Reset map view
    map.setView([18.5204, 73.8567], 11);
}

function findRoute() {
    const startSelect = document.getElementById('startSelect');
    const endSelect = document.getElementById('endSelect');
    const viaSelect = document.getElementById('viaSelect');

    const start = startSelect.value;
    const end = endSelect.value;
    const via = viaSelect.value;

    if (!start || !end) {
        alert('Please select both start and end locations');
        return;
    }

    if (start === end) {
        alert('Start and end locations must be different');
        return;
    }

    if (via && (via === start || via === end)) {
        alert('Via must be different from both start and end');
        return;
    }

    const routeResult = document.getElementById('routeResult');
    const routeInfo = document.getElementById('routeInfo');
    routeInfo.innerHTML = '<p>Calculating route...</p>';
    routeResult.style.display = 'block';

    const payload = { start, end };
    if (via) {
        payload.via = [via];
    }

    apiFetch(`${API_BASE}/api/route`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(data => {
        const algo = data.algorithm || 'Dijkstra';
        const corridor = data.via_chain && data.via_chain.length
            ? `<p><strong>Corridor:</strong> ${data.via_chain.map(escapeHtml).join(' → ')}</p>`
            : '';
        const note = data.constraint === 'via_waypoints'
            ? '<p><small>Chained shortest segments through each Via stop. Map line follows roads (OSRM) when available.</small></p>'
            : '<p><small>Edge weights are road driving times when you use Build Graph. Direct start→end is ignored unless you set Via. Red line follows roads (OSRM) when available.</small></p>';
        routeInfo.innerHTML = `
            <div class="route-summary">
                <h3>Shortest route (${algo})</h3>
                ${corridor}
                <p><strong>From:</strong> ${escapeHtml(data.path[0])}</p>
                <p><strong>To:</strong> ${escapeHtml(data.path[data.path.length - 1])}</p>
                <p><strong>Shortest-path total weight:</strong> ${data.total_time_minutes} ${escapeHtml(data.weight_unit || '')} (${data.total_time_formatted})</p>
                <p><small>Sum of edge weights on the path (auto-built graph uses OSRM road distances in km).</small></p>
                ${note}
                <p><strong>Stops on path:</strong> ${data.waypoints}</p>
                <h4>Order of visit</h4>
                <ol>
                    ${data.path.map(location => `<li>${escapeHtml(location)}</li>`).join('')}
                </ol>
            </div>
        `;
        
        drawRoute(data.path_coordinates, data.path, data.road_geometry);
    })
    .catch(error => {
        console.error('Error finding route:', error);
        routeInfo.innerHTML = `<p class="error">${error.message || 'Unable to find route.'}</p>`;
    });
}

function drawRoute(pathCoordinates, pathNames = [], roadGeometry = null) {
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }

    const routePoints = [];
    const routeMarkers = [];

    if (Array.isArray(pathCoordinates)) {
        pathCoordinates.forEach(coord => {
            if (coord && coord.coordinates && !Number.isNaN(coord.coordinates.lat) && !Number.isNaN(coord.coordinates.lng)) {
                routePoints.push([coord.coordinates.lat, coord.coordinates.lng]);
                routeMarkers.push(L.marker([coord.coordinates.lat, coord.coordinates.lng]).bindPopup(coord.name));
            }
        });
    }

    if (routePoints.length < 2 && Array.isArray(pathNames)) {
        pathNames.forEach(name => {
            const location = locations.find(loc => loc.name === name);
            if (location) {
                routePoints.push([location.lat, location.lng]);
                routeMarkers.push(L.marker([location.lat, location.lng]).bindPopup(name));
            }
        });
    }

    if (routePoints.length < 2) {
        return;
    }

    const useRoads = Array.isArray(roadGeometry) && roadGeometry.length >= 2;
    const linePoints = useRoads ? roadGeometry : routePoints;

    routeLayer = L.layerGroup();
    routeLayer.addLayer(L.polyline(linePoints, {
        color: '#ff0000',
        weight: 6,
        opacity: 0.85,
        smoothFactor: useRoads ? 0.85 : 1
    }));

    routeMarkers.forEach(marker => routeLayer.addLayer(marker));
    routeLayer.addTo(map);

    const bounds = L.latLngBounds(linePoints);
    map.fitBounds(bounds.pad(0.2));
}

function compareAlgorithms() {
    const startSelect = document.getElementById('algoStartSelect');
    const endSelect = document.getElementById('algoEndSelect');

    const start = startSelect.value;
    const end = endSelect.value;

    if (!start || !end) {
        alert('Please select both start and end locations for algorithm comparison');
        return;
    }

    if (start === end) {
        alert('Start and end locations must be different');
        return;
    }

    const comparisonDiv = document.getElementById('algorithmComparison');
    comparisonDiv.innerHTML = '<p style="text-align: center; padding: 20px;">Comparing algorithms... Please wait...</p>';
    comparisonDiv.style.display = 'block';

    apiFetch(`${API_BASE}/api/algorithms/compare`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ start, end })
    })
    .then(data => {
        displayAlgorithmComparison(data);
    })
    .catch(error => {
        console.error('Error comparing algorithms:', error);
        comparisonDiv.innerHTML = `<p style="color: #ef4444; padding: 10px;">Error: ${error.message || 'Could not compare algorithms.'}</p>`;
    });
}

function displayAlgorithmComparison(data) {
    const comparisonDiv = document.getElementById('algorithmComparison');
    let html = `
        <div class="comparison-header">
            <h3>Algorithm Comparison: ${escapeHtml(data.start)} → ${escapeHtml(data.end)}</h3>
        </div>
    `;

    // Extract algorithms data
    const algorithms = data.algorithms || {};
    const times = Object.values(algorithms).map(algo => algo.execution_time_ms);
    const fastest = Math.min(...times);

    // Create cards for each algorithm
    html += '<div class="algorithm-comparison">';

    // Dijkstra
    if (algorithms.dijkstra) {
        const algo = algorithms.dijkstra;
        const isFastest = algo.execution_time_ms === fastest;
        html += `
            <div class="algorithm-card dijkstra">
                <h3>⚡ Dijkstra</h3>
                <div class="algorithm-stat">
                    <strong>Time:</strong> ${algo.execution_time_ms.toFixed(2)} ms
                    <span class="time-badge ${isFastest ? 'fastest' : ''}">
                        ${isFastest ? '⭐ Fastest' : 'Speed: ' + algo.execution_time_ms.toFixed(2) + 'ms'}
                    </span>
                </div>
                <div class="algorithm-stat">
                    <strong>Distance:</strong> ${typeof algo.distance === 'number' ? algo.distance.toFixed(2) : 'N/A'}
                </div>
                <div class="algorithm-stat">
                    <strong>Complexity:</strong> ${escapeHtml(algo.complexity)}
                </div>
                <div class="algorithm-stat">
                    <strong>Path Length:</strong> ${algo.path.length} stops
                </div>
                <div class="algorithm-path">
                    <strong>Route:</strong> ${algo.path.map(escapeHtml).join(' → ')}
                </div>
            </div>
        `;
    }

    // Bellman-Ford
    if (algorithms.bellman_ford) {
        const algo = algorithms.bellman_ford;
        const isFastest = algo.execution_time_ms === fastest;
        html += `
            <div class="algorithm-card bellman-ford">
                <h3>🔄 Bellman-Ford</h3>
                <div class="algorithm-stat">
                    <strong>Time:</strong> ${algo.execution_time_ms.toFixed(2)} ms
                    <span class="time-badge ${isFastest ? 'fastest' : algo.has_negative_cycle ? 'slow' : ''}">
                        ${isFastest ? '⭐ Fastest' : algo.has_negative_cycle ? '⚠️ Neg. Cycle' : 'Speed: ' + algo.execution_time_ms.toFixed(2) + 'ms'}
                    </span>
                </div>
                <div class="algorithm-stat">
                    <strong>Distance:</strong> ${typeof algo.distance === 'number' ? algo.distance.toFixed(2) : 'N/A'}
                </div>
                <div class="algorithm-stat">
                    <strong>Complexity:</strong> ${escapeHtml(algo.complexity)}
                </div>
                <div class="algorithm-stat">
                    <strong>Path Length:</strong> ${algo.path.length} stops
                </div>
                ${algo.has_negative_cycle ? '<div class="algorithm-stat" style="color: #ef4444;"><strong>⚠️ Warning:</strong> Negative cycle detected!</div>' : ''}
                <div class="algorithm-path">
                    <strong>Route:</strong> ${algo.path.map(escapeHtml).join(' → ')}
                </div>
            </div>
        `;
    }

    // Floyd-Warshall
    if (algorithms.floyd_warshall) {
        const algo = algorithms.floyd_warshall;
        const isFastest = algo.execution_time_ms === fastest;
        html += `
            <div class="algorithm-card floyd-warshall">
                <h3>📊 Floyd-Warshall</h3>
                <div class="algorithm-stat">
                    <strong>Time:</strong> ${algo.execution_time_ms.toFixed(2)} ms
                    <span class="time-badge ${isFastest ? 'fastest' : algo.execution_time_ms > fastest * 2 ? 'slow' : ''}">
                        ${isFastest ? '⭐ Fastest' : 'Speed: ' + algo.execution_time_ms.toFixed(2) + 'ms'}
                    </span>
                </div>
                <div class="algorithm-stat">
                    <strong>Distance:</strong> ${typeof algo.distance === 'number' ? algo.distance.toFixed(2) : 'N/A'}
                </div>
                <div class="algorithm-stat">
                    <strong>Complexity:</strong> ${escapeHtml(algo.complexity)}
                </div>
                <div class="algorithm-stat">
                    <strong>Path Length:</strong> ${algo.path.length} stops
                </div>
                <div class="algorithm-stat">
                    <strong>Total Steps:</strong> ${algo.steps_count}
                </div>
                <div class="algorithm-path">
                    <strong>Route:</strong> ${algo.path.map(escapeHtml).join(' → ')}
                </div>
            </div>
        `;
    }

    html += '</div>';

    // Performance summary
    if (data.performance_summary) {
        const summary = data.performance_summary;
        html += `
            <div class="performance-summary">
                <p><strong>Performance Summary:</strong></p>
                <p>🏆 <strong>Fastest:</strong> ${escapeHtml(summary.fastest_algorithm.toUpperCase())} (${escapeHtml(algorithms[summary.fastest_algorithm].name)})</p>
                <p>🐢 <strong>Slowest:</strong> ${escapeHtml(summary.slowest_algorithm.toUpperCase())} (${escapeHtml(algorithms[summary.slowest_algorithm].name)})</p>
                <p>⏱️ <strong>Time Difference:</strong> ${summary.time_difference_ms.toFixed(2)} ms</p>
            </div>
        `;
    }

    comparisonDiv.innerHTML = html;
}

function loadStoredLocations() {
    const locationsList = document.getElementById('storedLocationsList');
    locationsList.innerHTML = '<p style="padding: 10px; text-align: center;">Loading stored locations...</p>';

    apiFetch(`${API_BASE}/api/locations/all`)
    .then(data => {
        if (!data.locations || data.locations.length === 0) {
            locationsList.innerHTML = '<p style="padding: 10px; text-align: center; color: #6b7280;">No stored locations yet.</p>';
            return;
        }

        let html = '';
        data.locations.forEach(loc => {
            html += `
                <div class="location-item" style="flex-direction: column; align-items: flex-start;">
                    <div style="width: 100%; margin-bottom: 5px;">
                        <strong>${escapeHtml(loc.name)}</strong>
                    </div>
                    <div style="width: 100%; font-size: 0.85rem; color: #6b7280;">
                        📍 ${loc.lat.toFixed(4)}, ${loc.lng.toFixed(4)}
                    </div>
                    <div style="width: 100%; font-size: 0.85rem; color: #6b7280;">
                        Source: ${escapeHtml(loc.geocode_source)} ${loc.matched_place ? '(' + escapeHtml(loc.matched_place.substring(0, 40)) + '...' + ')' : ''}
                    </div>
                </div>
            `;
        });

        locationsList.innerHTML = html;
    })
    .catch(error => {
        console.error('Error loading stored locations:', error);
        locationsList.innerHTML = `<p style="padding: 10px; color: #ef4444;">Error: ${error.message}</p>`;
    });
}

function updateAlgorithmSelects() {
    const algoStartSelect = document.getElementById('algoStartSelect');
    const algoEndSelect = document.getElementById('algoEndSelect');

    const currentStart = algoStartSelect.value;
    const currentEnd = algoEndSelect.value;

    algoStartSelect.innerHTML = '<option value="">Select Start Point</option>';
    algoEndSelect.innerHTML = '<option value="">Select End Point</option>';

    locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.name;
        option.textContent = location.name;

        algoStartSelect.appendChild(option);
        algoEndSelect.appendChild(option.cloneNode(true));
    });

    if (currentStart && locations.some(loc => loc.name === currentStart)) {
        algoStartSelect.value = currentStart;
    }
    if (currentEnd && locations.some(loc => loc.name === currentEnd)) {
        algoEndSelect.value = currentEnd;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    
    // Initialize UI
    updateEdgeSelects();
    updateAlgorithmSelects();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        map.invalidateSize();
    });
    
    // Handle Enter key in location input
    document.getElementById('locationInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addLocation();
        }
    });
    
    // Fix map size after tab change (if using tabs)
    setTimeout(() => {
        map.invalidateSize();
    }, 100);
});