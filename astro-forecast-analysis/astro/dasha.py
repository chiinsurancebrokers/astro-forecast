"""
Vimshottari Mahadasha / Antardasha calculator.
Standard 120-year cycle, balance-at-birth computed from Moon's nakshatra position.
"""
from datetime import datetime, timedelta
from .ephemeris import DASHA_ORDER, DASHA_YEARS, NAK_LORDS

YEAR_DAYS = 365.2425


def _add_years(start: datetime, years: float) -> datetime:
    return start + timedelta(days=years * YEAR_DAYS)


def moon_dasha_balance(moon_longitude):
    """
    Returns (starting_lord, elapsed_fraction) — how far into that lord's
    nakshatra span the Moon sits, used to compute the balance of the first dasha.
    """
    span = 360 / 27  # one nakshatra span
    nak_index = int(moon_longitude // span) % 27
    lord = NAK_LORDS[nak_index]
    position_in_nak = moon_longitude % span
    elapsed_fraction = position_in_nak / span
    return lord, elapsed_fraction


def build_mahadashas(birth_dt: datetime, moon_longitude, cycles=2):
    """
    Build a flat list of Mahadasha periods (with nested Antardasha) starting
    from birth, covering `cycles` full 120-year Vimshottari cycles (usually
    1 is enough for a lifetime; 2 gives headroom for long-range queries).
    """
    start_lord, elapsed = moon_dasha_balance(moon_longitude)
    start_idx = DASHA_ORDER.index(start_lord)

    # Balance of the first (birth) mahadasha
    full_years = DASHA_YEARS[start_lord]
    remaining_years = full_years * (1 - elapsed)

    periods = []
    cursor = birth_dt
    # first (partial) mahadasha
    md_end = _add_years(cursor, remaining_years)
    periods.append(_make_mahadasha(start_lord, cursor, md_end))
    cursor = md_end

    # subsequent full mahadashas
    idx = (start_idx + 1) % 9
    total_years_target = 120 * cycles
    years_used = remaining_years
    while years_used < total_years_target:
        lord = DASHA_ORDER[idx]
        yrs = DASHA_YEARS[lord]
        md_end = _add_years(cursor, yrs)
        periods.append(_make_mahadasha(lord, cursor, md_end))
        cursor = md_end
        years_used += yrs
        idx = (idx + 1) % 9

    return periods


def _make_mahadasha(lord, start, end):
    total_years = DASHA_YEARS[lord]
    antardashas = []
    idx = DASHA_ORDER.index(lord)
    ad_cursor = start
    for i in range(9):
        ad_lord = DASHA_ORDER[(idx + i) % 9]
        # antardasha length = (ad_lord years / 120) * mahadasha total years
        ad_years = (DASHA_YEARS[ad_lord] / 120.0) * total_years
        ad_end = _add_years(ad_cursor, ad_years)
        antardashas.append({
            "lord": ad_lord,
            "start": ad_cursor,
            "end": ad_end,
        })
        ad_cursor = ad_end
    return {
        "lord": lord,
        "start": start,
        "end": end,
        "antardashas": antardashas,
    }


def current_period(periods, at_dt: datetime):
    """Return (mahadasha, antardasha) active at the given datetime."""
    for md in periods:
        if md["start"] <= at_dt < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at_dt < ad["end"]:
                    return md, ad
            return md, md["antardashas"][-1]
    return None, None
