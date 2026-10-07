"""Vimshottari Mahadasha / Antardasha calculator.

Standard 120-year cycle, balance-at-birth computed from Moon's nakshatra
position. The first Mahadasha is handled as a clipped portion of the full
Mahadasha timeline so its Antardasha boundaries remain mathematically
consistent with the elapsed fraction at birth.
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
    span = 360 / 27
    nak_index = int(moon_longitude // span) % 27
    lord = NAK_LORDS[nak_index]
    position_in_nak = moon_longitude % span
    elapsed_fraction = position_in_nak / span
    return lord, elapsed_fraction


def build_mahadashas(birth_dt: datetime, moon_longitude, cycles=2):
    """
    Build Mahadasha periods (with nested Antardasha) from birth onward.

    Important: birth usually occurs part-way through the opening Mahadasha.
    We reconstruct that Mahadasha's theoretical full start, generate its true
    Antardasha sequence, then clip the already-elapsed portion at birth.
    """
    start_lord, elapsed = moon_dasha_balance(moon_longitude)
    start_idx = DASHA_ORDER.index(start_lord)

    full_years = DASHA_YEARS[start_lord]
    elapsed_years = full_years * elapsed
    remaining_years = full_years - elapsed_years

    # Reconstruct the full opening Mahadasha so the Antardasha boundaries are
    # based on the real full-period clock rather than restarted at birth.
    full_md_start = _add_years(birth_dt, -elapsed_years)
    full_md_end = _add_years(full_md_start, full_years)

    periods = [
        _make_mahadasha(
            start_lord,
            birth_dt,
            full_md_end,
            full_start=full_md_start,
        )
    ]
    cursor = full_md_end

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


def _make_mahadasha(lord, start, end, full_start=None):
    """
    Build Antardashas for a Mahadasha.

    When full_start precedes start, the Mahadasha is already in progress at
    birth. We generate the Antardashas from full_start and retain only the
    portions that overlap [start, end).
    """
    total_years = DASHA_YEARS[lord]
    sequence_start = full_start or start
    antardashas = []
    idx = DASHA_ORDER.index(lord)
    ad_cursor = sequence_start

    for i in range(9):
        ad_lord = DASHA_ORDER[(idx + i) % 9]
        ad_years = (DASHA_YEARS[ad_lord] / 120.0) * total_years
        ad_end = _add_years(ad_cursor, ad_years)

        overlap_start = max(start, ad_cursor)
        overlap_end = min(end, ad_end)
        if overlap_start < overlap_end:
            antardashas.append({
                "lord": ad_lord,
                "start": overlap_start,
                "end": overlap_end,
            })
        ad_cursor = ad_end

    # Floating-point year conversion can leave a tiny tail. Keep the timeline
    # continuous by extending the last AD to the declared MD end.
    if antardashas and antardashas[-1]["end"] < end:
        antardashas[-1]["end"] = end

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
            return md, md["antardashas"][-1] if md["antardashas"] else None
    return None, None
