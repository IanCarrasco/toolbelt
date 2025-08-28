import math
from typing import Optional, List, Dict, Any

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute haversine distance in kilometers between two points on the Earth.
    """
    R = 6371.0  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_walking_route(
    origin_name: Optional[str] = None,
    origin_latitude: Optional[float] = None,
    origin_longitude: Optional[float] = None,
    destination_name: Optional[str] = None,
    destination_latitude: Optional[float] = None,
    destination_longitude: Optional[float] = None,
    avoid_ferries: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Compute a walking route between two places (by name or coordinates).
    Returns whether a continuous land walking route exists and the route distance
    and segments (including necessary ferries).
    """
    # Determine human-friendly labels for start and end
    start_label = origin_name if origin_name else (
        f"Origin at ({origin_latitude}, {origin_longitude})" if origin_latitude is not None and origin_longitude is not None else "Origin"
    )
    end_label = destination_name if destination_name else (
        f"Destination at ({destination_latitude}, {destination_longitude})" if destination_latitude is not None and destination_longitude is not None else "Destination"
    )

    route_exists = False
    distance_km: float = 0.0
    distance_miles: float = 0.0
    requires_ferry_or_boat = False
    segments: List[Dict[str, Any]] = []
    summary = ""

    # Compute distance if coordinates are provided
    if (origin_latitude is not None and origin_longitude is not None and
        destination_latitude is not None and destination_longitude is not None):
        try:
            distance_km = _haversine(origin_latitude, origin_longitude, destination_latitude, destination_longitude)
        except Exception:
            distance_km = 0.0

        # If ferries are to be avoided and distance is very large, assume no land-only route
        if isinstance(avoid_ferries, bool) and avoid_ferries and distance_km > 15000.0:
            route_exists = False
            distance_km = 0.0
            distance_miles = 0.0
            segments = []
            summary = "No land-only walking route available when ferries are avoided."
        else:
            route_exists = True
            distance_miles = distance_km * 0.621371

            # In this simplified model, we treat as a single walking segment
            segments = [
                {
                    "mode": "walking",
                    "start": start_label,
                    "end": end_label,
                    "distance_km": distance_km
                }
            ]
            summary = f"Walking route from {start_label} to {end_label} computed."
            requires_ferry_or_boat = False  # No ferries in this simplified computation
    else:
        # Insufficient coordinate data to compute a distance
        route_exists = False
        distance_km = 0.0
        distance_miles = 0.0
        segments = []
        summary = "Insufficient location data: origin and destination coordinates are required for distance calculation."

    # Normalize numeric outputs
    if distance_km is None:
        distance_km = 0.0
    if distance_miles is None:
        distance_miles = 0.0

    return {
        "route_exists": route_exists,
        "distance_km": distance_km,
        "distance_miles": distance_miles,
        "requires_ferry_or_boat": requires_ferry_or_boat,
        "segments": segments,
        "summary": summary
    }