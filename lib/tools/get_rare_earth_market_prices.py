from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

# Mock base prices (USD per pound) for common rare earth elements
BASE_PRICE_MAP: Dict[str, float] = {
    'neodymium': 85.0, 'nd': 85.0,
    'praseodymium': 65.0, 'pr': 65.0,
    'dysprosium': 120.0, 'dy': 120.0,
    'terbium': 90.0, 'tb': 90.0,
    'yttrium': 12.0, 'y': 12.0,
    'lanthanum': 8.0, 'la': 8.0,
    'cerium': 10.0, 'ce': 10.0,
    'europium': 60.0, 'eu': 60.0,
    'samarium': 18.0, 'sm': 18.0,
    'gadolinium': 45.0, 'gd': 45.0,
    'holmium': 70.0, 'ho': 70.0,
    'erbium': 40.0, 'er': 40.0,
    'ytterbium': 48.0, 'yb': 48.0,
}

# Currency conversion mock rates relative to USD
CURRENCY_RATES: Dict[str, float] = {
    'USD': 1.0,
    'EUR': 0.92,
    'GBP': 0.78,
    'JPY': 157.0,
    'CNY': 7.1,
    'CAD': 1.35,
    'AUD': 1.50,
}


def _get_base_price_pound(element_key: str) -> float:
    key = element_key.lower()
    if key in BASE_PRICE_MAP:
        return BASE_PRICE_MAP[key]
    return 20.0 + (sum(ord(ch) for ch in key) % 50)


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt
    except Exception:
        return None


def _format_timestamp(dt: Optional[datetime], _date_str: Optional[str]) -> str:
    if dt is not None:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_unit(unit: str) -> str:
    if unit is None:
        return 'pound'
    u = unit.strip().lower()
    if u in ('pound', 'lbs', 'lb'):
        return 'pound'
    if u in ('kg', 'kilogram', 'kilograms'):
        return 'kg'
    return 'pound'


def get_rare_earth_market_prices(
    elements: List[str],
    currency: str,
    unit: str,
    date: Optional[str] = None,
    source: Optional[str] = None,
    include_spot_and_contract: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Fetches market prices for specified rare earth elements and returns prices per unit (e.g., per pound) in the requested currency,
    with source and timestamp. This is a mock implementation suitable for testing and demonstration.
    """
    currency_code = (currency or 'USD').upper()
    unit_norm = _normalize_unit(unit)
    date_dt = _parse_date(date)
    timestamp = _format_timestamp(date_dt, date)

    overall_source = source if source else 'Synthetic Mock Feed'
    element_list = list(elements or [])

    prices_output: List[Dict[str, Any]] = []

    def _make_price_item(
        element_name: str,
        usd_per_pound: float,
        per_pound_converted: float,
        per_unit_value: float,
        per_kg_value: Optional[float],
        ts: str,
        src: str,
        p_type: str,
        note: str
    ) -> Dict[str, Any]:
        return {
            'element': element_name,
            'price_per_unit': per_unit_value,
            'currency': currency_code,
            'unit': unit_norm,
            'price_per_kg': per_kg_value,
            'timestamp': ts,
            'source': src,
            'type_of_price': p_type,
            'notes': note
        }

    for elem in element_list:
        base_pound_usd = _get_base_price_pound(elem)

        factor = 1.0
        if date_dt is not None:
            factor += ((date_dt.month - 1) * 0.01) + ((date_dt.day - 1) * 0.001) + ((date_dt.year - 2000) * 0.0002)
        usd_per_pound = base_pound_usd * factor

        rate = CURRENCY_RATES.get(currency_code, 1.0)
        price_per_pound_cur = usd_per_pound * rate

        if unit_norm == 'pound':
            price_unit = price_per_pound_cur
            price_per_kg = price_unit * 2.2046226218
            price_item_spot = _make_price_item(
                elem, usd_per_pound, price_per_pound_cur, price_unit, price_per_kg,
                timestamp, overall_source, 'spot',
                'Synthetic price based on base value and date factor'
            )
            prices_output.append(price_item_spot)

            if include_spot_and_contract:
                contract_price = price_per_pound_cur * 1.06
                price_per_unit_contract = contract_price
                price_per_kg_contract = contract_price * 2.2046226218
                price_item_contract = _make_price_item(
                    elem, usd_per_pound, contract_price, price_per_unit_contract, price_per_kg_contract,
                    timestamp, overall_source, 'contract',
                    'Contract price including typical term premium'
                )
                prices_output.append(price_item_contract)
        else:  # unit_norm == 'kg'
            price_per_pound_for_kg = price_per_pound_cur
            price_per_unit_kg = price_per_pound_for_kg * 2.2046226218
            price_item_spot = _make_price_item(
                elem, usd_per_pound, price_per_pound_for_kg, price_per_unit_kg, price_per_unit_kg,
                timestamp, overall_source, 'spot',
                'Synthetic price based on base value and date factor'
            )
            prices_output.append(price_item_spot)

            if include_spot_and_contract:
                contract_price_per_pound = price_per_pound_for_kg * 1.06
                contract_price_per_unit_kg = contract_price_per_pound * 2.2046226218
                price_item_contract = _make_price_item(
                    elem, usd_per_pound, contract_price_per_pound, contract_price_per_unit_kg, contract_price_per_unit_kg,
                    timestamp, overall_source, 'contract',
                    'Contract price including typical term premium'
                )
                prices_output.append(price_item_contract)

    result = {
        'requested': {
            'elements': element_list,
            'currency': currency_code,
            'unit': unit_norm,
            'date': date
        },
        'prices': prices_output,
        'overall_source': overall_source
    }

    return result