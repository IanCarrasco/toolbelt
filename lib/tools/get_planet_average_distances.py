def get_planet_average_distances(reference_body: str, distance_type: str = "average") -> dict:
    """
    Return distances between a reference body (Sun or Earth) and each planet in the solar system.
    Distances are provided in kilometers and astronomical units (AU).

    Parameters:
    - reference_body: "Sun" or "Earth" (case-insensitive)
    - distance_type: "average" (default), "minimum", or "maximum"

    Returns:
    - dict mapping planet names to {"distance_km": float, "distance_au": float}
    """
    AU_KM = 149_597_870.7

    # Planetary data (AU)
    PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

    semi_major_au = {
        "Mercury": 0.387098337,
        "Venus": 0.72333199,
        "Earth": 1.0,
        "Mars": 1.52366231,
        "Jupiter": 5.20336301,
        "Saturn": 9.53707032,
        "Uranus": 19.19126393,
        "Neptune": 30.06992276
    }

    # Perihelion and aphelion distances (AU) - approximate values
    perihelion_au = {
        "Mercury": 0.3075,
        "Venus": 0.7184,
        "Earth": 0.9833,
        "Mars": 1.3814,
        "Jupiter": 4.95,
        "Saturn": 9.01,
        "Uranus": 18.33,
        "Neptune": 29.81
    }

    aphelion_au = {
        "Mercury": 0.4667,
        "Venus": 0.7282,
        "Earth": 1.0167,
        "Mars": 1.6668,
        "Jupiter": 5.459,
        "Saturn": 10.0,
        "Uranus": 20.11,
        "Neptune": 30.33
    }

    rb = (reference_body or "").strip().lower()
    if rb not in {"sun", "earth"}:
        raise ValueError("reference_body must be 'Sun' or 'Earth' (case-insensitive).")

    dt = (distance_type or "average").lower()
    if dt not in {"average", "minimum", "maximum"}:
        dt = "average"

    distances = {}

    for planet in PLANETS:
        if rb == "sun":
            # Distances from Sun: use semi-major axis for average, perihelion for minimum, aphelion for maximum
            if dt == "average":
                chosen_au = semi_major_au[planet]
            elif dt == "minimum":
                chosen_au = perihelion_au[planet]
            else:  # maximum
                chosen_au = aphelion_au[planet]
        else:  # rb == "earth"
            if planet == "Earth":
                # Distance from Earth to Earth is zero
                chosen_au = 0.0
            else:
                a = semi_major_au[planet]
                if dt == "average":
                    chosen_au = a
                elif dt == "minimum":
                    chosen_au = abs(a - 1.0)
                else:  # maximum
                    chosen_au = a + 1.0

        distance_km = chosen_au * AU_KM
        distances[planet] = {
            "distance_km": distance_km,
            "distance_au": chosen_au
        }

    return distances