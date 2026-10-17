"""Separate coordinate systems, with no blended probability or accuracy claim."""
from datetime import datetime, timezone
import swisseph as swe
from .ephemeris import build_natal_chart, planet_positions, sign_of, whole_sign_house_of
from .dasha import build_mahadashas, current_period

WESTERN_BODIES = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
}


def tropical_positions(jd):
    positions = {}
    for name, pid in WESTERN_BODIES.items():
        values, _ = swe.calc_ut(jd, pid, swe.FLG_MOSEPH | swe.FLG_SPEED)
        sign, degree = sign_of(values[0])
        positions[name] = dict(longitude=values[0], sign=sign,
                               sign_deg=degree, retrograde=values[3] < 0)
    return positions


def compare_methods(birth, at=None):
    at = at or datetime.now(timezone.utc)
    if at.tzinfo is None:
        raise ValueError('Comparison time must include a timezone.')
    at = at.astimezone(timezone.utc)
    chart = build_natal_chart(
        birth['year'], birth['month'], birth['day'], birth['hour'], birth['minute'],
        birth['utc_offset'], birth['latitude'], birth['longitude'])
    jd = chart['julian_day']
    western = tropical_positions(jd)
    _, axes = swe.houses_ex(jd, birth['latitude'], birth['longitude'], b'W', 0)
    asc_sign, asc_deg = sign_of(axes[0])
    for p in western.values():
        p['house'] = whole_sign_house_of(p['sign'], asc_sign)
    now_jd = swe.julday(at.year, at.month, at.day,
                       at.hour + at.minute / 60 + at.second / 3600)
    tropical_now = tropical_positions(now_jd)
    sidereal_now = planet_positions(now_jd)
    birth_dt = datetime(*(birth[k] for k in ('year','month','day','hour','minute')))
    # Dasha boundaries use the existing local civil-time convention.
    from datetime import timedelta
    local_at = (at + timedelta(hours=birth['utc_offset'])).replace(tzinfo=None)
    md, ad = current_period(build_mahadashas(birth_dt, chart['planets']['Moon']['longitude']), local_at)
    comparisons = []
    for name in ('Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn'):
        comparisons.append({'planet': name, 'western': western[name],
                            'vedic': chart['planets'][name]})
    # Contacts are coordinate geometry, not independent predictive votes.
    contacts = []
    for name in ('Jupiter','Saturn','Uranus','Neptune','Pluto'):
        for target in ('Sun','Moon','Mercury','Venus','Mars'):
            delta = abs((tropical_now[name]['longitude'] - western[target]['longitude'] + 180) % 360 - 180)
            for label, angle in (('conjunction',0),('sextile',60),('square',90),('trine',120),('opposition',180)):
                orb = abs(delta - angle)
                if orb <= 2:
                    contacts.append({'transit':name,'natal':target,'aspect':label,'orb':round(orb,3)})
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'as_of': at.isoformat(),
        'calculation': {'ephemeris':'Moshier', 'swisseph_version':swe.version,
                        'houses':'whole_sign', 'birth_ayanamsha_degrees':swe.get_ayanamsa_ut(jd),
                        'transit_ayanamsha_degrees':swe.get_ayanamsa_ut(now_jd),
                        'time_basis':'Explicit UTC offset supplied for the birth; comparison timestamp in UTC.'},
        'western': {'agent':'Western chart & transit geometry', 'zodiac':'tropical',
                    'ascendant':{'sign':asc_sign,'sign_deg':asc_deg},
                    'transits':tropical_now,'contacts':sorted(contacts,key=lambda x:x['orb']),
                    'scope':'Current transit contacts within 2 degrees; no progressions or solar returns in this view.'},
        'vedic': {'agent':'Vedic Timing — Lahiri & Vimshottari', 'zodiac':'sidereal',
                  'ayanamsha':'Lahiri','ascendant':chart['ascendant'],
                  'transits':sidereal_now,
                  'mahadasha':md['lord'] if md else None,
                  'antardasha':ad['lord'] if ad else None},
        'natal_comparison':comparisons,
        'interpretation_policy':[
            'Astronomical positions are calculated facts; astrological meanings are interpretations.',
            'Different sign labels reflect different coordinate origins, not a calculation error.',
            'Agreement between agents does not establish a probability or predictive accuracy.',
            'Shared planets and calculations make these evidence streams dependent, not independent votes.',
            'Neither system has demonstrated predictive superiority here; no combined confidence score is produced.'
        ],
    }
