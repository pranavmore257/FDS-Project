import java.io.Serializable;
import java.util.*;

/**
 * LocationHashtable: Stores and manages location data using Java's Hashtable
 * Provides persistent storage for locations with coordinates and metadata
 */
public class LocationHashtable implements Serializable {
    private static final long serialVersionUID = 1L;
    
    public static class Location implements Serializable {
        public String name;
        public double latitude;
        public double longitude;
        public String geocodeSource;
        public String matchedPlace;
        public long timestamp;
        
        public Location(String name, double latitude, double longitude, 
                       String geocodeSource, String matchedPlace) {
            this.name = name;
            this.latitude = latitude;
            this.longitude = longitude;
            this.geocodeSource = geocodeSource;
            this.matchedPlace = matchedPlace;
            this.timestamp = System.currentTimeMillis();
        }
        
        @Override
        public String toString() {
            return "Location{" +
                    "name='" + name + '\'' +
                    ", lat=" + latitude +
                    ", lng=" + longitude +
                    ", source='" + geocodeSource + '\'' +
                    ", matched='" + matchedPlace + '\'' +
                    '}';
        }
    }
    
    private Hashtable<String, Location> locations;
    
    public LocationHashtable() {
        this.locations = new Hashtable<>();
    }
    
    /**
     * Add a location to the hashtable
     */
    public synchronized void addLocation(String name, double latitude, double longitude,
                                       String geocodeSource, String matchedPlace) {
        Location loc = new Location(name, latitude, longitude, geocodeSource, matchedPlace);
        locations.put(name.toLowerCase(), loc);
    }
    
    /**
     * Retrieve a location by name
     */
    public synchronized Location getLocation(String name) {
        return locations.get(name.toLowerCase());
    }
    
    /**
     * Check if location exists
     */
    public synchronized boolean hasLocation(String name) {
        return locations.containsKey(name.toLowerCase());
    }
    
    /**
     * Remove a location
     */
    public synchronized Location removeLocation(String name) {
        return locations.remove(name.toLowerCase());
    }
    
    /**
     * Get all locations
     */
    public synchronized Hashtable<String, Location> getAllLocations() {
        return new Hashtable<>(locations);
    }
    
    /**
     * Clear all locations
     */
    public synchronized void clearAll() {
        locations.clear();
    }
    
    /**
     * Get all location names
     */
    public synchronized List<String> getAllLocationNames() {
        return new ArrayList<>(locations.keySet());
    }
    
    /**
     * Get count of stored locations
     */
    public synchronized int getLocationCount() {
        return locations.size();
    }
    
    /**
     * Export hashtable as String for debugging
     */
    @Override
    public synchronized String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("LocationHashtable{\n");
        locations.forEach((key, loc) -> 
            sb.append("  ").append(key).append(": ").append(loc).append("\n")
        );
        sb.append("}");
        return sb.toString();
    }
}
