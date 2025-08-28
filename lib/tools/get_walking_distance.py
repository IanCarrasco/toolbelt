import json
import math
import urllib.parse
import urllib.request
from typing import Optional, Tuple, Dict


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance between two points on the Earth using the haversine formula.
    Returns distance in meters.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def geocode_place(place: str) -> Optional[Tuple[float, float]]:
    """
    Geocode a place name or address using Nominatim (OpenStreetMap).
    Returns (latitude, longitude) if found, otherwise None.
    """
    if not place:
        return None

    base_url = "https://nominatim.openstreetmap.org/search"
    query = urllib.parse.urlencode({"q": place, "format": "json", "limit": 1})
    url = f"{base_url}?{query}"

    headers = {"User-Agent": "WalkingDistanceBot/1.0"}

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            data = json.loads(content)
            if isinstance(data, list) and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)
    except Exception:
        pass

    return None


def get_walking_distance(origin: str, destination: str) -> Dict[str, float]:
    """
    Returns the walking route distance between two places in meters.
    If an exact walking route is not available, falls back to great-circle distance.

    Parameters:
        origin: Origin place name or address (e.g., "New York, NY")
        destination: Destination place name or address (e.g., "Los Angeles, CA")

    Returns:
        dict with key "distance_meters" and value as float distance in meters
    """
    if origin is None or destination is None:
        raise ValueError("Origin and destination must be provided.")

    origin = origin.strip()
    destination = destination.strip()

    if origin == "" or destination == "":
        raise ValueError("Origin and destination must be non-empty strings.")

    # If origin and destination are the same, distance is zero
    if origin.lower() == destination.lower():
        return {"distance_meters": 0.0}

    # Geocode origin and destination
    o_coords = geocode_place(origin)
    d_coords = geocode_place(destination)

    if o_coords is None or d_coords is None:
        raise ValueError("Unable to geocode origin or destination.")

    lat1, lon1 = o_coords
    lat2, lon2 = d_coords

    # Try to fetch walking route distance from OSRM (public demo server)
    osrm_url = (
        "http://router.project-osrm.org/route/v1/foot/"
        f"{lon1:.6f},{lat1:.6f};{lon2:.6f},{lat2:.6f}"
        "?overview=false"
    )

    req = urllib.request.Request(osrm_url, headers={"User-Agent": "WalkingDistanceBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            data = json.loads(content)
            if isinstance(data, dict) and data.get("code") == "Ok":
                routes = data.get("routes", [])
                if routes and isinstance(routes, list):
                    distance = float(routes[0].get("distance", 0.0))
                    return {"distance_meters": distance}
    except Exception:
        # If OSRM request fails, fall back to great-circle distance
        pass

    # Fallback: great-circle (haversine) distance
    gc_distance = haversine_distance_meters(lat1, lon1, lat2, lon2)
    return {"distance_meters": gc_distance}