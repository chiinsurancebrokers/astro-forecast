"""
Raw transit activation-score engine.

IMPORTANT: these are heuristic, uncalibrated 0-100 scores meant as a
starting point for calibration against real outcomes -- not a validated
predictive model. Mirrors the life-area taxonomy used in prior reports
so historical calibration data stays comparable.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .ephemeris import (
    PLANET_IDS, SIGNS, sign_of, whole_sign_house_of, local_to_julian_ut, EPHE_FLAGS,
)
import swisseph as swe

# Life areas -> the natal houses whose transit activation feeds them.
# Houses use standard Vedic significations.
AREA_HOUSES = {
    "career": [10, 6, 1],
    "money": [2, 11],
    "sudden_gain": [11, 8],
    "financial_risk": [8, 12, 6],
    "business": [10, 7, 11],
    "love": [5, 7],
    "marriage_commitment": [7, 8],
    "sex_chemistry": [5, 8],
    "travel_foreign": [9, 12],
    "home_property": [4, 2],
    "luxury_assets": [4, 2, 11],
    "major_change": [1, 8, 12],
    "socialization": [11, 3, 7],
    "earned_income": [2, 6, 10],
    "claims_settlements": [6, 8],
    "external_money": [2, 11, 8],
    "spending_loss_risk": [12, 8, 6],
    "social_isolation": [12, 8, 6],
    "social_friction": [6, 7, 8],
}

# Planet base weight: benefics push scores up on "growth" areas,
# malefics push up "risk" areas (this is intentional -- a Saturn/Mars/
# Rahu transit through a risk house raises the risk score, not lowers it).
BENEFIC = {"Jupiter", "Venus", "Moon", "Mercury"}
MALEFIC = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

RISK_AREAS = {"financial_risk", "spending_loss_risk", "social_isolation", "social_friction"}

# Only these transiting bodies are slow enough to matter for a monthly
# resolution report; the Moon washes out at monthly granularity.
TRANSIT_BODIES = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]


def _transiting_house(jd_ut, planet_name, asc_sign):
    if planet_name == "Ketu":
        (lon, *_r), _f = swe.calc_ut(jd_ut, swe.MEAN_NODE, EPHE_FLAGS)
        lon = (lon + 180) % 360
    else:
        (lon, *_r), _f = swe.calc_ut(jd_ut, PLANET_IDS[planet_name], EPHE_FLAGS)
    sign, _deg = sign_of(lon)
    return whole_sign_house_of(sign, asc_sign)


def _month_score(jd_ut, asc_sign, dasha_lord=None, antardasha_lord=None):
    """Raw 0-100 score per area for a single sampled date."""
    house_pressure = {h: 0.0 for h in range(1, 13)}
    for body in TRANSIT_BODIES:
        house = _transiting_house(jd_ut, body, asc_sign)
        weight = 1.3 if body in MALEFIC else 1.0
        # dasha lord transiting its own dasha house gets extra weight
        if body == dasha_lord:
            weight *= 1.6
        elif body == antardasha_lord:
            weight *= 1.3
        house_pressure[house] += weight

    scores = {}
    for area, houses in AREA_HOUSES.items():
        raw = sum(house_pressure[h] for h in houses)
        # normalize: max plausible raw ~ (8 bodies * 1.3 * 1.6) spread over
        # up to 3 houses -> squash into 0-100 with a soft ceiling
        pct = min(100.0, (raw / (len(houses) * 3.0)) * 100.0)
        scores[area] = round(pct, 1)
    return scores


def monthly_forecast(natal_chart, latitude, longitude, start: datetime, months: int,
                      dasha_periods=None):
    """
    Returns { "YYYY-MM": { area: score, ... }, ... } for `months` months
    starting at `start` (uses the 15th of each month as the sample date).
    """
    asc_sign = natal_chart["ascendant"]["sign"]
    results = {}
    cursor = start.replace(day=15)
    for _ in range(months):
        jd = local_to_julian_ut(cursor.year, cursor.month, cursor.day, 12, 0, 0)
        dasha_lord = antar_lord = None
        if dasha_periods:
            from .dasha import current_period
            md, ad = current_period(dasha_periods, cursor)
            if md:
                dasha_lord = md["lord"]
            if ad:
                antar_lord = ad["lord"]
        results[cursor.strftime("%Y-%m")] = _month_score(jd, asc_sign, dasha_lord, antar_lord)
        cursor = cursor + relativedelta(months=1)
    return results


def house_change_calendar(start: datetime, months: int, latitude=None, longitude=None,
                           step_days=1):
    """
    Scan Jupiter, Saturn, Rahu, Ketu, Mars for the sign (house) they occupy,
    day by day, and emit each date a sign change is detected. Mirrors the
    'Major Planet House-Change Calendar' section of prior reports.
    """
    end = start + relativedelta(months=months)
    bodies = ["Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
    last_sign = {}
    events = []
    cursor = start
    while cursor <= end:
        jd = local_to_julian_ut(cursor.year, cursor.month, cursor.day, 12, 0, 0)
        for body in bodies:
            if body == "Ketu":
                (lon, lat_, dist_, lon_speed, *_rest), _f = swe.calc_ut(jd, swe.MEAN_NODE, EPHE_FLAGS | swe.FLG_SPEED)
                lon = (lon + 180) % 360
                retro = lon_speed >= 0  # Ketu retrograde flag mirrors Rahu's (inverted)
            else:
                (lon, lat_, dist_, lon_speed, *_rest), _f = swe.calc_ut(jd, PLANET_IDS[body], EPHE_FLAGS | swe.FLG_SPEED)
                retro = lon_speed < 0
            sign, _deg = sign_of(lon)
            prev = last_sign.get(body)
            if prev and prev != sign:
                events.append({
                    "date": cursor.strftime("%Y-%m-%d"),
                    "planet": body,
                    "from_sign": prev,
                    "to_sign": sign,
                    "retrograde": retro,
                })
            last_sign[body] = sign
        cursor = cursor + relativedelta(days=step_days)
    return events
