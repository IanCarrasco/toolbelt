from typing import List, Dict, Any

def get_rare_earth_elements(include_scandium_yttrium: bool = True) -> List[Dict[str, Any]]:
    """
    Return a list of rare earth elements (the 15 lanthanides; optionally include Scandium and Yttrium)
    with basic properties.

    Each element dictionary contains:
    - name: element name
    - symbol: element symbol
    - atomic_number: atomic number
    - atomic_weight: standard atomic weight (approximate)

    Parameters:
    - include_scandium_yttrium: If True, include Scandium (Sc) and Yttrium (Y) in the returned list.

    Returns:
    - List of element dictionaries. The order is Sc, Y (optional), followed by La through Lu.
    """

    elements: List[Dict[str, Any]] = []

    if include_scandium_yttrium:
        elements.extend([
            {"name": "Scandium", "symbol": "Sc", "atomic_number": 21, "atomic_weight": 44.95591},
            {"name": "Yttrium", "symbol": "Y", "atomic_number": 39, "atomic_weight": 88.90584},
        ])

    elements.extend([
        {"name": "Lanthanum", "symbol": "La", "atomic_number": 57, "atomic_weight": 138.90547},
        {"name": "Cerium", "symbol": "Ce", "atomic_number": 58, "atomic_weight": 140.116},
        {"name": "Praseodymium", "symbol": "Pr", "atomic_number": 59, "atomic_weight": 140.90765},
        {"name": "Neodymium", "symbol": "Nd", "atomic_number": 60, "atomic_weight": 144.242},
        {"name": "Promethium", "symbol": "Pm", "atomic_number": 61, "atomic_weight": 145.0},
        {"name": "Samarium", "symbol": "Sm", "atomic_number": 62, "atomic_weight": 150.36},
        {"name": "Europium", "symbol": "Eu", "atomic_number": 63, "atomic_weight": 151.964},
        {"name": "Gadolinium", "symbol": "Gd", "atomic_number": 64, "atomic_weight": 157.25},
        {"name": "Terbium", "symbol": "Tb", "atomic_number": 65, "atomic_weight": 158.92535},
        {"name": "Dysprosium", "symbol": "Dy", "atomic_number": 66, "atomic_weight": 162.500},
        {"name": "Holmium", "symbol": "Ho", "atomic_number": 67, "atomic_weight": 164.93033},
        {"name": "Erbium", "symbol": "Er", "atomic_number": 68, "atomic_weight": 167.259},
        {"name": "Thulium", "symbol": "Tm", "atomic_number": 69, "atomic_weight": 168.934},
        {"name": "Ytterbium", "symbol": "Yb", "atomic_number": 70, "atomic_weight": 173.045},
        {"name": "Lutetium", "symbol": "Lu", "atomic_number": 71, "atomic_weight": 174.9668},
    ])

    return elements