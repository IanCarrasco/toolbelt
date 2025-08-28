import math

# Semi-major axis (average orbital radius) in astronomical units (AU)
PLANETS_AU = {
    'Mercury': 0.387,
    'Venus': 0.723,
    'Earth': 1.0,
    'Mars': 1.524,
    'Jupiter': 5.203,
    'Saturn': 9.537,
    'Uranus': 19.191,
    'Neptune': 30.069
}

AU_KM = 149597870.7  # kilometers in 1 AU

def _average_distance_au(r1_au: float, r2_au: float, samples: int = 360) -> float:
    """
    Numerical approximation of the mean distance between two bodies with circular coplanar orbits
    as their relative true anomaly theta varies from 0 to pi.
    D(theta) = sqrt(r1^2 + r2^2 - 2*r1*r2*cos(theta))
    """
    if samples < 2:
        return abs(r1_au - r2_au)
    total = 0.0
    for i in range(samples):
        theta = math.pi * i / (samples - 1)
        cos_theta = math.cos(theta)
        D = math.sqrt(r1_au * r1_au + r2_au * r2_au - 2.0 * r1_au * r2_au * cos_theta)
        total += D
    return total / float(samples)

def get_planet_distances(starting_body: str, distance_type: str, units: str = 'km'):
    """
    Return distance estimates between the starting_body and each other major body in PLANETS_AU.
    Distances are computed under a circular-coplanar orbit approximation.

    Parameters:
    - starting_body: Name of the starting body (e.g., 'Earth', 'Mars'). The function will report
                     distances to all other major bodies defined in PLANETS_AU excluding the starting body.
    - distance_type: 'closest' | 'average' | 'farthest'
        - 'closest'  -> minimum possible distance |r1 - r2|
        - 'average'  -> mean distance over relative orbital positions
        - 'farthest' -> maximum possible distance r1 + r2
    - units: 'km' or 'au' (output distances in kilometers or astronomical units)

    Returns:
    A dictionary with:
      - distances: mapping from target body name to distance value in requested units
      - unit: the unit used for the returned distances ('km' or 'au')
      - distance_type: echo of the requested distance_type
      - notes: textual notes about the assumptions
    """
    if distance_type not in {'closest', 'average', 'farthest'}:
        raise ValueError("distance_type must be one of 'closest', 'average', or 'farthest'.")

    body = starting_body.strip().title()
    if body not in PLANETS_AU:
        raise ValueError(f"Unknown starting body '{starting_body}'. Supported bodies: {', '.join(sorted(PLANETS_AU.keys()))}.")

    if units not in {'km', 'au'}:
        raise ValueError("units must be 'km' or 'au'.")

    # Distances are from starting_body to all other major bodies (exclude the starting body itself)
    r1_au = PLANETS_AU[body]

    targets = [p for p in PLANETS_AU.keys() if p != body]

    distances = {}
    for target in targets:
        r2_au = PLANETS_AU[target]

        if distance_type == 'closest':
            d_au = abs(r1_au - r2_au)
        elif distance_type == 'farthest':
            d_au = r1_au + r2_au
        else:  # 'average'
            d_au = _average_distance_au(r1_au, r2_au, samples=360)

        if units == 'km':
            distances[target] = d_au * AU_KM
        else:
            distances[target] = d_au

    notes = (
        "Assumes circular, coplanar orbits around the Sun. "
        "Distances are approximate estimates derived from simple geometric relations. "
        f"Computed with {len(targets)} target bodies. "
        "Epoch effects and orbital eccentricities are neglected."
    )

    return {
        "distances": distances,
        "unit": units,
        "distance_type": distance_type,
        "notes": notes
    }