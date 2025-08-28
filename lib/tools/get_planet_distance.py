import math

AU_KM = 149_597_870.7  # kilometers in one astronomical unit

# Approximate orbital semi-major axes (in AU) for planets (including Pluto for optional use)
PLANET_AU = {
    'Mercury': 0.387,
    'Venus': 0.723,
    'Earth': 1.0,
    'Mars': 1.524,
    'Jupiter': 5.203,
    'Saturn': 9.537,
    'Uranus': 19.191,
    'Neptune': 30.07,
    'Pluto': 39.48  # optional, not a planet by current IAU definition
}


def get_planet_distance(planet: str, method: str, units: str = 'au') -> dict:
    """
    Estimate the distance between Earth and another planet using orbital semi-major axes.

    Parameters:
    - planet: Target planet name (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto optional).
    - method: 'closest' for approximate minimum distance, 'average' for mean Earth–planet distance,
              'farthest' for approximate maximum distance.
    - units: 'km' or 'au' for the output units (default 'au').

    Returns:
    - dict with keys:
      - distance_km: distance in kilometers
      - distance_au: distance in astronomical units
      - explanation: textual explanation of the estimate
    """
    if not isinstance(planet, str):
        raise TypeError("The 'planet' parameter must be a string.")
    if not isinstance(method, str):
        raise TypeError("The 'method' parameter must be a string.")

    planet_key = planet.strip().title()
    if planet_key not in PLANET_AU:
        raise ValueError(f"Unknown or unsupported planet '{planet}'. Supported: {', '.join(sorted(PLANET_AU.keys()))}.")

    method_key = method.strip().lower()
    if method_key not in {'closest', 'average', 'farthest'}:
        raise ValueError("The 'method' parameter must be one of: 'closest', 'average', 'farthest'.")

    units_key = units.strip().lower() if isinstance(units, str) else 'au'
    if units_key not in {'km', 'au'}:
        raise ValueError("The 'units' parameter must be either 'km' or 'au'.")

    r_earth = 1.0  # AU
    r_planet = PLANET_AU[planet_key]

    if method_key == 'closest':
        distance_au = abs(r_planet - r_earth)
        explanation = (
            f"Closest Earth–{planet_key} distance occurs when both bodies share the same heliocentric longitude "
            f"(approximately aligned on the same side of the Sun). Distance = |{r_earth} - {r_planet}| AU = {distance_au:.6f} AU."
        )
    elif method_key == 'farthest':
        distance_au = r_earth + r_planet
        explanation = (
            f"Farthest Earth–{planet_key} distance occurs when the planets lie on opposite sides of the Sun (heliocentric longitudes differ by ~180°). "
            f"Distance = {r_earth} + {r_planet} AU = {distance_au:.6f} AU."
        )
    else:  # average
        # Approximate average distance by sampling orbital phase difference Δλ from 0 to 2π
        samples = 1000
        total = 0.0
        for i in range(samples):
            theta = (2 * math.pi) * (i + 0.5) / samples
            d = math.sqrt(r_earth**2 + r_planet**2 - 2 * r_earth * r_planet * math.cos(theta))
            total += d
        distance_au = total / samples
        explanation = (
            f"Average Earth–{planet_key} distance estimated by sampling orbital phase (Δλ) from 0 to 2π with r_Earth={r_earth} AU and "
            f"r_{planet_key}={r_planet} AU. Approximate mean distance ≈ {distance_au:.6f} AU."
        )

    distance_km = distance_au * AU_KM

    return {
        'distance_km': distance_km,
        'distance_au': distance_au,
        'explanation': explanation
    }