/**
 * Frontend JavaScript for Dijkstra Route Finder
 * Handles map interactions, API calls, and UI updates
 */

const API_BASE_URL = 'http://localhost:5000/api';

// Global variables
let map;
let markers = [];
let routePolyline = null;
let locations = [];
let locationMarkers = {};
let autocomplete;
let geocoder;
let locationPriorities = {}; // { locationName: number }
let nextPriority = 1;
let directionsService;
let directionsRenderer;

// Initialize Google Map
function initMap() {
    // Center map on Pune city
    const puneCenter = { lat: 18.5204, lng: 73.8567 };
    
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: puneCenter,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true
    });

    // Initialize Directions services for road-following routes
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        preserveViewport: false
    });

    // Initialize autocomplete for location input
    const input = document.getElementById('locationInput');
    autocomplete = new google.maps.places.Autocomplete(input, {
        componentRestrictions: { country: 'in' },
        fields: ['formatted_address', 'geometry', 'name'],
        types: ['geocode']
    });

    // Initialize geocoder
    geocoder = new google.maps.Geocoder();

    // Click on map to add a location (reverse geocode)
    map.addListener('click', async (e) => {
        const latlng = { lat: e.latLng.lat(), lng: e.latLng.lng() };
        try {
            const result = await geocoder.geocode({ location: latlng });
            if (result.status === 'OK' && result.results && result.results.length > 0) {
                // Prefer formatted_address within Pune
                const addr = result.results[0].formatted_address;
                addLocationByName(addr);
            } else {
                // Fallback to raw coords label
                addLocationByName(`Point (${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)})`);
            }
        } catch (err) {
            console.error('Reverse geocoding failed', err);
        }
    });

    // Clear loading message
    document.getElementById('mapLoading').style.display = 'none';
}

// Add location to the list
async function addLocation() {
    const input = document.getElementById('locationInput');
    const locationName = input.value.trim();

    if (!locationName) {
        alert('Please enter a location name');
        return;
    }

    if (locations.includes(locationName)) {
        alert('Location already added');
        return;
    }

    await addLocationByName(locationName, () => { input.value = ''; });
}

// Shared helper to add a location by name via backend and update UI
async function addLocationByName(locationName, onSuccessClearCb) {
    if (!locationName || locations.includes(locationName)) {
        if (!locationName) return;
        alert('Location already added');
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/locations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: locationName })
        });
        const data = await response.json();
        if (response.ok) {
            locations.push(locationName);
            // assign default priority
            locationPriorities[locationName] = nextPriority++;
            updateLocationsList();
            updateSelectOptions();
            addMarkerToMap(locationName, data.coordinates);
            // auto-build graph
            await buildGraph();
            // auto-select start/end based on priority
            autoSelectStartEndByPriority();
            if (onSuccessClearCb) onSuccessClearCb();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error adding location:', error);
        alert('Failed to add location. Make sure the backend server is running.');
    }
}

// Remove location from list
function removeLocation(locationName) {
    locations = locations.filter(loc => loc !== locationName);
    delete locationPriorities[locationName];
    updateLocationsList();
    updateSelectOptions();
    removeMarkerFromMap(locationName);
    buildGraph();
    autoSelectStartEndByPriority();
}

// Update locations list in UI
function updateLocationsList() {
    const listContainer = document.getElementById('locationsList');
    
    if (locations.length === 0) {
        listContainer.innerHTML = '<div class="empty-state">No locations added yet</div>';
        return;
    }

    // sort by priority ascending for display consistency
    const sorted = [...locations].sort((a, b) => (locationPriorities[a] || 0) - (locationPriorities[b] || 0));
    listContainer.innerHTML = sorted.map(location => `
        <div class="location-item">
            <span>${location}</span>
            <div style="display:flex; align-items:center; gap:8px;">
                <label style="font-size:0.9em;color:#555;">Priority</label>
                <input type="number" min="1" value="${locationPriorities[location] || ''}" style="width:70px; padding:6px; border:1px solid #ccc; border-radius:6px;" onchange="updatePriority('${location}', this.value)">
                <button class="remove-btn" onclick="removeLocation('${location}')">Remove</button>
            </div>
        </div>
    `).join('');
}

// Update select options for start/end points
function updateSelectOptions() {
    const startSelect = document.getElementById('startSelect');
    const endSelect = document.getElementById('endSelect');
    const edgeFromSelect = document.getElementById('edgeFromSelect');
    const edgeToSelect = document.getElementById('edgeToSelect');

    // Clear existing options (except first option)
    startSelect.innerHTML = '<option value="">Select Start Point</option>';
    endSelect.innerHTML = '<option value="">Select End Point</option>';
    if (edgeFromSelect) edgeFromSelect.innerHTML = '<option value="">From</option>';
    if (edgeToSelect) edgeToSelect.innerHTML = '<option value="">To</option>';

    // Add location options
    const sorted = [...locations].sort((a, b) => (locationPriorities[a] || 0) - (locationPriorities[b] || 0));
    sorted.forEach(location => {
        const option1 = new Option(location, location);
        const option2 = new Option(location, location);
        startSelect.add(option1);
        endSelect.add(option2);
        if (edgeFromSelect) edgeFromSelect.add(new Option(location, location));
        if (edgeToSelect) edgeToSelect.add(new Option(location, location));
    });
}

// Add a custom edge via backend
async function addEdge() {
    const from = document.getElementById('edgeFromSelect').value;
    const to = document.getElementById('edgeToSelect').value;
    const weightStr = document.getElementById('edgeWeight').value;
    const bidirectional = document.getElementById('edgeBidirectional').checked;
    // Default metric for auto-weight is distance (kilometers)
    const metric = 'distance';

    if (!from || !to) {
        alert('Please select both From and To locations');
        return;
    }
    if (from === to) {
        alert('From and To must be different');
        return;
    }
    let body;
    if (weightStr && weightStr.trim() !== '') {
        const weight = parseFloat(weightStr);
        if (!Number.isFinite(weight) || weight <= 0) {
            alert('Please enter a valid positive weight (minutes)');
            return;
        }
        body = { from, to, weight, bidirectional };
    } else {
        // No weight provided: request backend to compute real weight from map
        body = { from, to, bidirectional, metric };
    }

    try {
        const response = await fetch(`${API_BASE_URL}/edges`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await response.json();
        if (response.ok) {
            alert('Edge added successfully');
            // Optionally re-run findRoute if start/end are selected
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (err) {
        console.error('Error adding edge', err);
        alert('Failed to add edge. Ensure backend is running.');
    }
}

// Update a location's priority and auto rebuild
function updatePriority(locationName, value) {
    const num = parseInt(value, 10);
    if (Number.isNaN(num) || num < 1) return;
    locationPriorities[locationName] = num;
    updateLocationsList();
    updateSelectOptions();
    autoSelectStartEndByPriority();
    buildGraph();
}

// Auto-select start/end based on min/max priority
function autoSelectStartEndByPriority() {
    if (locations.length < 2) return;
    const sorted = [...locations].sort((a, b) => (locationPriorities[a] || 0) - (locationPriorities[b] || 0));
    const start = sorted[0];
    const end = sorted[sorted.length - 1];
    const startSelect = document.getElementById('startSelect');
    const endSelect = document.getElementById('endSelect');
    startSelect.value = start || '';
    endSelect.value = end || '';
}

// Build graph from locations
async function buildGraph() {
    if (locations.length < 2) {
        alert('Please add at least 2 locations before building the graph');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/locations/build-graph`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // default: use only custom edges (no complete all-pairs graph)
            body: JSON.stringify({ locations: locations, mode: 'custom_edges_only' })
        });

        const data = await response.json();

        if (response.ok) {
            alert(`Graph built successfully!\nMode: ${data.mode}\nVertices: ${data.vertices}\nEdges: ${data.edges}`);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error building graph:', error);
        alert('Failed to build graph. Make sure the backend server is running.');
    }
}

// Find shortest route using Dijkstra's algorithm
async function findRoute() {
    const start = document.getElementById('startSelect').value;
    const end = document.getElementById('endSelect').value;

    if (!start || !end) {
        alert('Please select both start and end points');
        return;
    }

    if (start === end) {
        alert('Start and end points must be different');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/route`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ start: start, end: end })
        });

        const data = await response.json();

        if (response.ok) {
            displayRoute(data);
            drawRouteOnMap(data.path_coordinates);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error finding route:', error);
        alert('Failed to find route. Make sure the backend server is running.');
    }
}

// Display route information
function displayRoute(routeData) {
    const routeResult = document.getElementById('routeResult');
    const routeInfo = document.getElementById('routeInfo');

    routeResult.style.display = 'block';

    routeInfo.innerHTML = `
        <div class="time-info">
            ⏱️ Total Time: ${routeData.total_time_formatted}
        </div>
        <div class="route-path">
            <h3>Route Path:</h3>
            <ol class="route-steps">
                ${routeData.path.map((location, index) => `
                    <li>${location}</li>
                `).join('')}
            </ol>
        </div>
        <div style="margin-top: 10px; color: #666; font-size: 0.9em;">
            Total Waypoints: ${routeData.waypoints}
        </div>
    `;
}

// Add marker to map
function addMarkerToMap(locationName, coordinates) {
    const marker = new google.maps.Marker({
        position: { lat: coordinates.lat, lng: coordinates.lng },
        map: map,
        title: locationName,
        label: {
            text: String(locations.length),
            color: 'white',
            fontWeight: 'bold'
        },
        icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
        }
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `<strong>${locationName}</strong>`
    });

    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });

    locationMarkers[locationName] = marker;
    markers.push(marker);
}

// Remove marker from map
function removeMarkerFromMap(locationName) {
    if (locationMarkers[locationName]) {
        locationMarkers[locationName].setMap(null);
        delete locationMarkers[locationName];
        markers = markers.filter(m => m !== locationMarkers[locationName]);
    }
}

// Draw route on map
function drawRouteOnMap(pathCoordinates) {
    if (!pathCoordinates || pathCoordinates.length < 2) {
        return;
    }

    // Prepare origin, destination and waypoints for Directions API
    const origin = new google.maps.LatLng(pathCoordinates[0].coordinates.lat, pathCoordinates[0].coordinates.lng);
    const destination = new google.maps.LatLng(
        pathCoordinates[pathCoordinates.length - 1].coordinates.lat,
        pathCoordinates[pathCoordinates.length - 1].coordinates.lng
    );
    const waypoints = pathCoordinates.slice(1, -1).map(p => ({
        location: new google.maps.LatLng(p.coordinates.lat, p.coordinates.lng),
        stopover: true
    }));

    const request = {
        origin,
        destination,
        waypoints,
        travelMode: google.maps.TravelMode.DRIVING,
        optimizeWaypoints: false,
        provideRouteAlternatives: false
    };

    directionsService.route(request, (result, status) => {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(result);

            // Update markers styling for start/intermediate/end
            pathCoordinates.forEach((coord, index) => {
                const marker = locationMarkers[coord.name];
                if (marker) {
                    let iconUrl, labelColor;
                    if (index === 0) {
                        iconUrl = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
                        labelColor = 'white';
                    } else if (index === pathCoordinates.length - 1) {
                        iconUrl = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png';
                        labelColor = 'white';
                    } else {
                        iconUrl = 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
                        labelColor = 'black';
                    }
                    marker.setIcon({ url: iconUrl });
                    marker.setLabel({ text: String(index + 1), color: labelColor, fontWeight: 'bold' });
                }
            });
        } else {
            console.error('Directions request failed:', status);
        }
    });
}

// Clear all data
function clearAll() {
    if (confirm('Are you sure you want to clear all locations and routes?')) {
        locations = [];
        markers.forEach(marker => marker.setMap(null));
        markers = [];
        locationMarkers = {};
        
        if (routePolyline) {
            routePolyline.setMap(null);
            routePolyline = null;
        }

        updateLocationsList();
        updateSelectOptions();
        document.getElementById('routeResult').style.display = 'none';
        document.getElementById('locationInput').value = '';
        
        // Reset map to Pune center
        map.setCenter({ lat: 18.5204, lng: 73.8567 });
        map.setZoom(12);
    }
}

// Allow Enter key to add location
document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('locationInput');
    
    locationInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addLocation();
        }
    });

    // Initialize empty state
    updateLocationsList();
});

