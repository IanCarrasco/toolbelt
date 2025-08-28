from typing import Optional, Dict, Any

def geocode_place(place_name: str, country_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve a place name into geographic coordinates and a standardized place identifier.

    Returns a dictionary with the following keys:
    - standard_name: str
    - latitude: float
    - longitude: float
    - place_id: Optional[str]
    - confidence: float (0.0 - 1.0)

    This implementation uses a small built-in dataset for demonstration purposes.
    If the place cannot be found, a ValueError is raised.
    """
    dataset = {
        # key: (standard_name, lat, lon, place_id)
        "new york": ("New York, NY, USA", 40.7128, -74.0060, "geoNYC"),
        "los angeles": ("Los Angeles, CA, USA", 34.0522, -118.2437, "geoLA"),
        "london": ("London, United Kingdom", 51.5074, -0.1278, "geoLDN"),
        "paris": ("Paris, France", 48.8566, 2.3522, "geoPAR"),
        "tokyo": ("Tokyo, Japan", 35.6895, 139.6917, "geoTYO"),
        "berlin": ("Berlin, Germany", 52.52, 13.4050, "geoBER"),
        "san francisco": ("San Francisco, CA, USA", 37.7749, -122.4194, "geoSFO"),
        "sf": ("San Francisco, CA, USA", 37.7749, -122.4194, "geoSFO"),
        "sydney": ("Sydney, Australia", -33.8688, 151.2093, "geoSYD"),
        "melbourne": ("Melbourne, Australia", -37.8136, 144.9631, "geoMEL"),
        "rome": ("Rome, Italy", 41.9028, 12.4964, "geoROM"),
        "toronto": ("Toronto, Canada", 43.6532, -79.3832, "geoTOR"),
    }

    key = place_name.strip().lower()

    def make_result(rec: tuple, confidence: float) -> Dict[str, Any]:
        standard_name, lat, lon, pid = rec
        return {
            "standard_name": standard_name,
            "latitude": lat,
            "longitude": lon,
            "place_id": pid,
            "confidence": confidence
        }

    # Exact match
    if key in dataset:
        rec = dataset[key]
        country_match = False
        if country_hint:
            country_hint_lc = country_hint.strip().lower()
            country_match = country_hint_lc in rec[0].lower()
        conf = 0.99 if country_match else 0.95
        return make_result(rec, conf)

    # Fuzzy-like match: if the input contains any known key
    for known_key, rec in dataset.items():
        if known_key in key:
            country_match = False
            if country_hint:
                country_hint_lc = country_hint.strip().lower()
                country_match = country_hint_lc in rec[0].lower()
            conf = 0.95 if country_match else 0.85
            return make_result(rec, conf)

    # If nothing found, raise an error
    raise ValueError(f"Unable to geocode place_name: {place_name}")