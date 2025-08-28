import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _iso_now() -> str:
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


def fetch_fire_relevant_data(
    latitude: float,
    longitude: float,
    radius_km: Optional[float] = 5.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timestamp: Optional[str] = None,
    data_providers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch environmental, vegetation, historical fire, and human-landcover data relevant to wildfire risk
    for a location and time window.

    This implementation provides deterministic, synthetic data suitable for testing and demonstration
    without external dependencies. It mirrors the structure described in the tool schema.
    """

    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required inputs.")

    if radius_km is None:
        radius_km = 5.0
    try:
        radius_km = float(radius_km)
        if radius_km <= 0:
            radius_km = 5.0
    except (TypeError, ValueError):
        radius_km = 5.0

    if data_providers is None:
        data_providers = ["local_estimates"]

    # Observation time
    observation_time = timestamp if timestamp is not None else _iso_now()
    forecast_hours = 24

    # Weather (synthetic but deterministic with lat/lon)
    temperature_c = round(10.0 + (abs(latitude) * 0.4) + (radius_km * 0.2), 1)
    relative_humidity_pct = round(50.0 + math.sin(math.radians(latitude)) * 20.0, 1)
    wind_speed_ms = round(2.0 + abs(math.cos(math.radians(longitude))) * 3.0, 1)
    wind_direction_deg = int((abs(latitude) * 5.0) % 360)
    precipitation_mm = round(max(0.0, math.sin(math.radians(latitude)) * math.cos(math.radians(longitude)) * 5.0), 2)

    weather = {
        "temperature_c": temperature_c,
        "relative_humidity_pct": clamp(relative_humidity_pct, 0.0, 100.0),
        "wind_speed_ms": wind_speed_ms,
        "wind_direction_deg": wind_direction_deg,
        "precipitation_mm": max(0.0, precipitation_mm),
        "observation_time": observation_time,
        "forecast_hours": forecast_hours,
    }

    # Vegetation indices (synthetic)
    ndvi = clamp(0.2 + (abs(latitude) * 0.01) + (abs(longitude) * 0.005), 0.0, 0.95)
    evi = clamp(ndvi * 0.85 + 0.05, 0.0, 1.0)
    live_fuel_moisture_pct = clamp(40.0 + (abs(latitude) % 10) * 2.0 - (radius_km * 0.5), 5.0, 100.0)
    satellite_time = _iso_now()

    vegetation = {
        "ndvi": ndvi,
        "evi": evi,
        "live_fuel_moisture_pct": live_fuel_moisture_pct,
        "satellite_time": satellite_time,
    }

    # Drought index (synthetic)
    kbdi = round(max(0.0, (abs(latitude) % 40) * 2.0 + (radius_km * 0.5) - 5.0), 2)
    spi = round(((abs(latitude) + abs(longitude)) % 8) - 2, 2)
    reference_time = _iso_now()

    drought_index = {
        "kbdi": kbdi,
        "spi": spi,
        "reference_time": reference_time,
    }

    # Historical fires within radius (synthetic)
    base_count = int((abs(latitude) + abs(longitude)) % 15)
    fire_count = max(0, base_count)
    last_fire_dates: List[str] = []
    today = datetime.utcnow().date()
    for i in range(fire_count):
        d = today - timedelta(days=i * 7)
        last_fire_dates.append(d.strftime("%Y-%m-%d"))

    historical_fires = {
        "fire_count": fire_count,
        "last_fire_dates": last_fire_dates,
    }

    # Land cover and fuel model (synthetic)
    cover_options = ["Forest", "Grassland", "Shrubland", "Agriculture", "Urban"]
    dominant_class = cover_options[int((abs(latitude) * 13 + abs(longitude) * 7) % len(cover_options))]
    fuel_model_code = f"FM-{abs(int((latitude * longitude) % 9)) + 1:02d}"

    landcover = {
        "dominant_class": dominant_class,
        "fuel_model_code": fuel_model_code,
    }

    # Topography (synthetic)
    elevation_m = round(200.0 + (abs(latitude) * 5.0) + (radius_km * 12.0), 1)
    slope_deg = round((abs(longitude) % 30.0) + (radius_km * 0.2), 1)
    aspect_deg = int((abs(latitude) * 3.0) % 360)

    topography = {
        "elevation_m": elevation_m,
        "slope_deg": slope_deg,
        "aspect_deg": aspect_deg,
    }

    # Human factors (synthetic)
    population_density_per_km2 = round(30.0 + (abs(latitude) % 5) * 8.0, 1)
    distance_to_nearest_road_m = round(1000.0 + (radius_km * 150.0), 1)
    known_ignition_points = [
        {
            "name": "ignition_point_alpha",
            "lat": round(latitude + 0.01, 6),
            "lon": round(longitude + 0.01, 6),
        },
        {
            "name": "ignition_point_beta",
            "lat": round(latitude - 0.02, 6),
            "lon": round(longitude - 0.03, 6),
        },
    ]

    human_factors = {
        "population_density_per_km2": population_density_per_km2,
        "distance_to_nearest_road_m": distance_to_nearest_road_m,
        "known_ignition_points": known_ignition_points,
    }

    metadata = {
        "retrieval_time": _iso_now(),
        "providers_used": data_providers,
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "start_date": start_date,
        "end_date": end_date,
        "timestamp_requested": timestamp,
    }

    # Assemble final result
    result: Dict[str, Any] = {
        "weather": weather,
        "vegetation": vegetation,
        "drought_index": drought_index,
        "historical_fires": historical_fires,
        "landcover": landcover,
        "topography": topography,
        "human_factors": human_factors,
        "metadata": metadata,
    }

    return result