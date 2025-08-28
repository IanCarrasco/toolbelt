def geocode_location(query: str, country: str = None) -> dict:
    """
    Convert a free-form location into a standardized address and latitude/longitude.
    Uses OpenStreetMap Nominatim as the geocoding service.

    Returns a dictionary with keys:
      - address: standardized address string (display_name from Nominatim)
      - latitude: float latitude
      - longitude: float longitude
      - place_id: string place identifier (from Nominatim)
    If nothing is found or an error occurs, values may be None.
    """
    import json
    import urllib.request
    import urllib.parse

    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
    }
    if country:
        params["countrycodes"] = country

    url = base_url + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "GeocodeLocationTool/1.0 (example@example.com)"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            results = json.loads(content)

            if not isinstance(results, list) or len(results) == 0:
                return {"address": None, "latitude": None, "longitude": None, "place_id": None}

            first = results[0]
            address = first.get("display_name")
            latitude = first.get("lat")
            longitude = first.get("lon")
            place_id = first.get("place_id")

            return {
                "address": address,
                "latitude": float(latitude) if latitude is not None else None,
                "longitude": float(longitude) if longitude is not None else None,
                "place_id": str(place_id) if place_id is not None else None,
            }
    except Exception:
        return {"address": None, "latitude": None, "longitude": None, "place_id": None}