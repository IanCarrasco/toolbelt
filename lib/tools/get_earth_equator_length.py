import math

def get_earth_equator_length():
    """
    Return the length of Earth's equator using a standard reference (WGS84). No inputs required.
    """
    # WGS84 equatorial radius in kilometers
    a_km = 6378.137
    circumference_km = 2.0 * math.pi * a_km  # equatorial circumference in km

    # Convert to miles
    km_to_miles = 0.621371192237334
    circumference_miles = circumference_km * km_to_miles

    return {
        "distance_km": round(circumference_km, 3),
        "distance_miles": round(circumference_miles, 3),
        "reference": "WGS84"
    }