"""
Core sidereal (Lahiri) chart calculations using the Swiss Ephemeris.
Whole Sign house system, Vedic planet set (Sun..Saturn + Rahu/Ketu).
"""
import swisseph as swe
from datetime import datetime, timedelta

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,  # mean node; Ketu = Rahu + 180
}

# Force the built-in Moshier analytical ephemeris explicitly everywhere.
# Without this, calc_ut/houses_ex look for external .se1 data files on
# disk and behavior differs across hosts depending on whether those files
# happen to be present -- Moshier needs no external files and is accurate
# to a few arcseconds, more than sufficient here. This constant is ORed
# into every ephemeris call in this module and in astro/forecast.py.
EPHE_FLAGS = swe.FLG_SIDEREAL | swe.FLG_MOSEPH

# Vimshottari dasha order and years
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"] * 3


def init_ephemeris(ephe_path=None):
    """Set sidereal mode (Lahiri) once at startup. Call before any calc."""
    if ephe_path:
        swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(swe.SIDM_LAHIRI)


def local_to_julian_ut(year, month, day, hour, minute, utc_offset_hours):
    """Convert local civil time + UTC offset to a Julian Day (UT)."""
    decimal_hour = hour + minute / 60.0
    ut_hour = decimal_hour - utc_offset_hours
    return swe.julday(year, month, day, ut_hour)


def sign_of(longitude):
    idx = int(longitude // 30) % 12
    return SIGNS[idx], longitude % 30


def nakshatra_of(longitude):
    span = 360 / 27
    idx = int(longitude // span) % 27
    pada = int((longitude % span) // (span / 4)) + 1
    return NAKSHATRAS[idx], pada, idx


def planet_positions(jd_ut):
    """Return dict: planet -> {longitude, sign, sign_deg, nakshatra, pada, retrograde}"""
    flags = EPHE_FLAGS | swe.FLG_SPEED
    out = {}
    for name, pid in PLANET_IDS.items():
        (lon, lat, dist, lon_speed, *_rest), _flag = swe.calc_ut(jd_ut, pid, flags)
        sign, sign_deg = sign_of(lon)
        nak, pada, _ = nakshatra_of(lon)
        out[name] = {
            "longitude": lon,
            "sign": sign,
            "sign_deg": sign_deg,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": lon_speed < 0,
        }
    # Ketu = Rahu + 180
    rahu_lon = out["Rahu"]["longitude"]
    ketu_lon = (rahu_lon + 180) % 360
    sign, sign_deg = sign_of(ketu_lon)
    nak, pada, _ = nakshatra_of(ketu_lon)
    out["Ketu"] = {
        "longitude": ketu_lon, "sign": sign, "sign_deg": sign_deg,
        "nakshatra": nak, "pada": pada, "retrograde": True,
    }
    return out


def ascendant(jd_ut, latitude, longitude):
    """Whole-sign ascendant: returns (asc_longitude, asc_sign)."""
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', EPHE_FLAGS)
    asc_lon = ascmc[0]
    sign, sign_deg = sign_of(asc_lon)
    return asc_lon, sign, sign_deg


def whole_sign_house_of(planet_sign, asc_sign):
    """House number (1-12) of a planet under Whole Sign houses."""
    return (SIGNS.index(planet_sign) - SIGNS.index(asc_sign)) % 12 + 1


def build_natal_chart(year, month, day, hour, minute, utc_offset_hours, latitude, longitude):
    jd = local_to_julian_ut(year, month, day, hour, minute, utc_offset_hours)
    planets = planet_positions(jd)
    asc_lon, asc_sign, asc_deg = ascendant(jd, latitude, longitude)
    for p in planets.values():
        p["house"] = whole_sign_house_of(p["sign"], asc_sign)
    moon_nak_idx = nakshatra_of(planets["Moon"]["longitude"])[2]
    return {
        "julian_day": jd,
        "ascendant": {"longitude": asc_lon, "sign": asc_sign, "sign_deg": asc_deg},
        "planets": planets,
        "moon_nakshatra_index": moon_nak_idx,
    }
