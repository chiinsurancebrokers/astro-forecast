"""Vimshottari Mahadasha / Antardasha calculator.

Standard 120-year cycle, balance-at-birth computed from the Moon's
nakshatra position.

The birth Mahadasha is normally already in progress. Its Antardashas are
therefore built from the hypothetical full Mahadasha start and clipped at
birth, so the active Antardasha at birth is preserved correctly instead of
restarting the Antardasha sequence on the birth date.
"""
from datetime import datetime, timedelta
from .ephemeris import DASHA_ORDER, DASHA_YEARS, NAK_LORDS

YEAR_DAYS = 365.2425


def _add_years(start: datetime, years: float) -> datetime:
    return start + timedelta(days=years * YEAR_DAYS)


def moon_dasha_balance(moon_longitude):
    """Return (starting_lord, elapsed_fraction) within the Moon's nakshatra."""
    span = 360 / 27
    nak_index = int(moon_longitude // span) % 27
    lord = NAK_LORDS[nak_index]
    position_in_nak = moon_longitude % span
    elapsed_fraction = position_in_nak / span
    return lord, elapsed_fraction


def _full_antardashas(lord, full_start):
    """Build the nine Antardashas for one complete Mahadasha."""
    total_years = DASHA_YEARS[lord]
    idx = DASHA_ORDER.index(lord)
    out = []
    cursor = full_start
    for i in range(9):
        ad_lord = DASHA_ORDER[(idx + i) % 9]
        ad_years = (DASHA_YEARS[ad_lord] / 120.0) * total_years
        end = _add_years(cursor, ad_years)
        out.append({"lord": ad_lord, "start": cursor, "end": end})
        cursor = end
    return out


def _make_mahadasha(lord, start, end, full_start=None):
    """Create one Mahadasha and clip its Antardashas to the visible interval."""
    full_start = full_start or start
    antardashas = []
    for ad in _full_antardashas(lord, full_start):
        clipped_start = max(ad["start"], start)
        clipped_end = min(ad["end"], end)
        if clipped_start < clipped_end:
            antardashas.append({
                "lord": ad["lord"],
                "start": clipped_start,
                "end": clipped_end,
            })
    return {
        "lord": lord,
        "start": start,
        "end": end,
        "antardashas": antardashas,
    }


def build_mahadashas(birth_dt: datetime, moon_longitude, cycles=2):
    """Build Mahadasha periods from birth with correctly clipped birth-period ADs."""
    start_lord, elapsed = moon_dasha_balance(moon_longitude)
    start_idx = DASHA_ORDER.index(start_lord)

    full_years = DASHA_YEARS[start_lord]
    elapsed_years = full_years * elapsed
    remaining_years = full_years - elapsed_years

    # Reconstruct where the current Mahadasha actually began, then clip to birth.
    full_md_start = _add_years(birth_dt, -elapsed_years)
    first_md_end = _add_years(full_md_start, full_years)

    periods = [
        _make_mahadasha(
            start_lord,
            birth_dt,
            first_md_end,
            full_start=full_md_start,
        )
    ]

    cursor = first_md_end
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


def current_period(periods, at_dt: datetime):
    """Return (Mahadasha, Antardasha) active at the requested datetime."""
    for md in periods:
        if md["start"] <= at_dt < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at_dt < ad["end"]:
                    return md, ad
            return md, md["antardashas"][-1] if md["antardashas"] else None
    return None, None
