import datetime
from typing import List, Dict, Any, Optional


def fetch_material_market_prices(
    materials: List[str],
    unit: Optional[str] = None,
    currency: Optional[str] = None,
    date: Optional[str] = None,
    include_alternatives: bool = False
) -> Dict[str, Any]:
    """
    Fetch current market prices for one or more materials from market data sources.

    Returns a mapping of material name to price information.

    Parameters:
    - materials: list of material names (e.g., 'neodymium', 'praseodymium', 'yttrium', 'cerium oxide', 'NdFeB')
    - unit: desired reported unit ('per_lb', 'per_kg', 'per_metric_ton'); defaults to 'per_kg' if omitted
    - currency: desired currency code (e.g., 'USD', 'EUR'); defaults to 'USD' if omitted
    - date: ISO date (YYYY-MM-DD) for historical price; if omitted, latest/spot price is returned
    - include_alternatives: if True, include common alternative forms in notes (oxide, alloy)
    """

    if not materials:
        return {"prices": {}}

    # Helpers
    def parse_date(d: str) -> Optional[datetime.date]:
        try:
            return datetime.date.fromisoformat(d)
        except Exception:
            return None

    def usd_per_unit_to_target(price_per_kg_usd: float, to_unit: str) -> float:
        to = to_unit.lower()
        if to in (None, '', 'per_kg'):
            return price_per_kg_usd
        if to == 'per_lb':
            return price_per_kg_usd / 2.2046226218  # 1 kg = 2.2046... lb
        if to == 'per_metric_ton':
            return price_per_kg_usd * 1000.0
        # Unknown unit, default to per_kg
        return price_per_kg_usd

    def usd_to_currency(amount_usd: float, to_currency: Optional[str]) -> float:
        if to_currency is None:
            return amount_usd
        to = to_currency.upper()
        # Simple mock FX rates: 1 USD = X units of target currency
        rates = {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79,
            'JPY': 158.0,
            'CAD': 1.36,
            'CNY': 7.2,
        }
        rate = rates.get(to, 1.0)
        return amount_usd * rate

    # Default unit/currency
    unit_final = unit if unit is not None else 'per_kg'
    currency_final = currency if currency is not None else 'USD'

    # Timestamp handling
    now_utc = datetime.datetime.utcnow()
    date_obj = parse_date(date) if date is not None else None
    if date_obj:
        delta_days = (datetime.date.today() - date_obj).days
        # bounded factor to avoid extreme values
        factor = max(0.8, min(1.5, 1.0 + 0.01 * delta_days))
        timestamp_str = date_obj.isoformat() + "T12:00:00Z"
    else:
        factor = 1.0
        timestamp_str = now_utc.replace(microsecond=0).isoformat() + "Z"

    # Known base prices in USD per kilogram
    known_prices = {
        'neodymium': 60.0,
        'praseodymium': 70.0,
        'yttrium': 30.0,
        'cerium oxide': 25.0,
        'ndfeb': 125.0,  # NdFeB alloy/magnet price proxy
        'ndfeb magnets': 125.0,
    }

    def base_price_per_kg(material_name: str) -> float:
        key = material_name.strip().lower()
        if key in known_prices:
            return float(known_prices[key])
        # Deterministic fallback for unknown materials
        s = sum(ord(ch) for ch in material_name)
        return float(5.0 + (s % 400))  # range roughly 5 - 404 USD/kg

    prices_output: Dict[str, Dict[str, Any]] = {}

    for mat in materials:
        if not isinstance(mat, str) or mat.strip() == "":
            continue
        base_price_kg_usd = base_price_per_kg(mat) * factor  # apply historical factor

        # Convert to requested unit
        price_per_target_unit_usd = usd_per_unit_to_target(base_price_kg_usd, unit_final)

        # Convert currency
        final_price = usd_to_currency(price_per_target_unit_usd, currency_final)

        # Round to 2 decimals for readability
        final_price_rounded = round(final_price, 2)

        price_entry: Dict[str, Any] = {
            "price": final_price_rounded,
            "unit": unit_final,
            "currency": currency_final,
            "source": "MockMarketData API",
            "timestamp": timestamp_str
        }

        # Optional alternatives in notes
        if include_alternatives:
            oxide_name = f"{mat} oxide"
            alloy_name = f"{mat} alloy" if mat.lower() != "ndfeb" else "Nd-Fe-B alloy"
            oxide_price_usd = base_price_kg_usd * 1.05  # oxide typically slightly higher
            alloy_price_usd = base_price_kg_usd * 1.15

            oxide_price = usd_to_currency(usd_per_unit_to_target(oxide_price_usd, unit_final), currency_final)
            alloy_price = usd_to_currency(usd_per_unit_to_target(alloy_price_usd, unit_final), currency_final)

            oxide_price = round(oxide_price, 2)
            alloy_price = round(alloy_price, 2)

            notes = (
                f"Alternatives: oxide {oxide_name} (~{oxide_price} {currency_final}/{unit_final}); "
                f"alloy {alloy_name} (~{alloy_price} {currency_final}/{unit_final})."
            )
            price_entry["notes"] = notes

        prices_output[mat] = price_entry

    return {"prices": prices_output}