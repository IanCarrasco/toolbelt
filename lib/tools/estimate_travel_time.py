import math
from typing import Optional, Tuple, Dict

def estimate_travel_time(
    start_location: str,
    end_location: str,
    mode: str = "walking",
    speed_m_per_s: Optional[float] = None,
    distance_method: str = "route"
) -> Dict[str, object]:
    """
    Estimate travel distance and time between two locations for a given mode.
    - distance_method: 'straight_line' or 'route'
    - If speed_m_per_s is provided, it is used directly. Otherwise, mode-specific defaults are used:
      walking: 1.4 m/s, bicycling: 4.5 m/s, driving: 13.9 m/s.
    - For 'route' method, a rough road-distance factor is applied when coordinates are known.
    
    Returns a dict with:
      - distance_meters: float
      - time_seconds: float
      - time_readable: str
      - used_speed_m_per_s: float
      - method_explanation: str
    """
    # Built-in approximate coordinates for common cities (lat, lon)
    CITY_COORDS: Dict[str, Tuple[float, float]] = {
        "New York": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "San Francisco": (37.7749, -122.4194),
        "London": (51.5074, -0.1278),
        "Paris": (48.8566, 2.3522),
        "Tokyo": (35.6895, 139.6917),
        "Berlin": (52.52, 13.405),
        "Sydney": (-33.8688, 151.2093),
        "Madrid": (40.4168, -3.7038),
        "Chicago": (41.8781, -87.6298),
        "Toronto": (43.6532, -79.3832),
        "Singapore": (1.3521, 103.8198),
        "Delhi": (28.6139, 77.2090),
        "Paris, France": (48.8566, 2.3522),
    }

    def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        # Returns distance in meters
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def parse_coords(location: str) -> Optional[Tuple[float, float]]:
        s = location.strip()
        # Direct lat,lon pattern: "lat, lon"
        import re
        m = re.match(r'^(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$', s)
        if m:
            lat = float(m.group(1))
            lon = float(m.group(2))
            return (lat, lon)
        # City name lookup
        if s in CITY_COORDS:
            return CITY_COORDS[s]
        # Try a case-insensitive match for known keys
        for key, val in CITY_COORDS.items():
            if s.lower() == key.lower():
                return val
        return None

    # Determine speeds
    mode_lower = (mode or "walking").lower()
    if speed_m_per_s is not None:
        used_speed = float(speed_m_per_s)
        speed_from_mode = True
    else:
        speed_from_mode = False
        if mode_lower == "walking":
            used_speed = 1.4
        elif mode_lower in ("bicycling", "cycling"):
            used_speed = 4.5
        elif mode_lower == "driving" or mode_lower == "car":
            used_speed = 13.9
        else:
            # default to walking if unknown
            used_speed = 1.4

    # Acquire coordinates
    start_coords = parse_coords(start_location)
    end_coords = parse_coords(end_location)

    distance_meters: Optional[float] = None
    method_explanation_parts = []

    if start_coords is not None and end_coords is not None:
        straight_dist = haversine(start_coords, end_coords)
        if distance_method.lower() == "straight_line":
            distance_meters = straight_dist
            method_explanation_parts.append("Computed straight-line (great-circle) distance using provided coordinates.")
        else:  # route
            # Rough route-distance estimate based on straight-line distance
            route_factor = 1.25  # generic factor to account for roads
            distance_meters = straight_dist * route_factor
            method_explanation_parts.append("Estimated route distance by applying a rough road-distance factor to the straight-line distance (external routing service not used).")
        method_explanation = " ".join(method_explanation_parts)
    else:
        # Attempt to salvage with known city coordinates if one of them is missing
        missing = []
        if start_coords is None:
            missing.append("start_location")
        if end_coords is None:
            missing.append("end_location")
        if missing:
            method_explanation = (
                "Unable to determine coordinates for: " +
                ", ".join(missing) +
                ". Provide coordinates in 'lat,lon' format or use known city names "
                "that are included in the built-in mapping (e.g., 'New York', 'London')."
            )
            # As a safe fallback, try to compute using any available coordinates (partial)
            if start_coords is not None and end_coords is not None:
                distance_meters = haversine(start_coords, end_coords)
            else:
                distance_meters = None
        else:
            distance_meters = None
            method_explanation = "Insufficient data to compute distance."

    # Compute time if distance known
    if distance_meters is not None and used_speed > 0:
        time_seconds = distance_meters / used_speed
        def format_duration(seconds: float) -> str:
            if seconds < 0:
                seconds = 0
            days, rem = divmod(int(seconds), 86400)
            hours, rem = divmod(rem, 3600)
            minutes, secs = divmod(rem, 60)
            parts = []
            if days:
                parts.append(f"{days} days")
            if hours:
                parts.append(f"{hours} hours")
            if minutes:
                parts.append(f"{minutes} minutes")
            if secs:
                parts.append(f"{secs} seconds")
            return " ".join(parts) if parts else "0 seconds"

        time_readable = format_duration(time_seconds)
    else:
        time_seconds = None
        time_readable = None

    # If we explicitly computed distance, prepare explanation
    if distance_meters is not None:
        method_explanation = (method_explanation or "") + (
            " Using speed: {:.3f} m/s.".format(used_speed)
            if speed_meters := used_speed else ""
        )

    # Build result
    result = {
        "distance_meters": distance_meters,
        "time_seconds": time_seconds,
        "time_readable": time_readable,
        "used_speed_m_per_s": used_speed,
        "method_explanation": (method_explanation.strip() if method_explanation else "")
    }
    return result

# Example usage (uncomment to test):
# print(estimate_travel_time("New York", "Los Angeles", mode="driving"))
# print(estimate_travel_time("New York", "San Francisco", distance_method="straight_line"))
# print(estimate_travel_time("40.7128,-74.0060", "34.0522,-118.2437"))