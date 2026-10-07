"""Deterministic evidence helpers for the interpretation layer.

This module does not predict events. It extracts auditable natal evidence from
the already-calculated sidereal/Lahiri chart so the LLM can explain *why* a
signal receives weight instead of relying on generic prose.
"""

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra",
}

DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries",
}

ANGLE_ASPECTS = {
    "conjunction": (0.0, 8.0),
    "sextile": (60.0, 5.0),
    "square": (90.0, 7.0),
    "trine": (120.0, 7.0),
    "opposition": (180.0, 8.0),
}

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}


def _angular_distance(a, b):
    d = abs(float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def _dignity(name, sign):
    if name not in EXALTATION:
        return "node_or_other"
    if SIGN_RULERS.get(sign) == name:
        return "own_sign"
    if EXALTATION.get(name) == sign:
        return "exalted"
    if DEBILITATION.get(name) == sign:
        return "debilitated"
    return "neutral"


def natal_planet_evidence(chart):
    out = []
    for name, p in chart["planets"].items():
        house = int(p["house"])
        tags = []
        if house in KENDRA:
            tags.append("kendra")
        if house in TRIKONA:
            tags.append("trikona")
        if house in DUSTHANA:
            tags.append("dusthana")
        if p.get("retrograde"):
            tags.append("retrograde")
        out.append({
            "planet": name,
            "sign": p["sign"],
            "house": house,
            "longitude": round(float(p["longitude"]), 4),
            "dignity": _dignity(name, p["sign"]),
            "tags": tags,
            "nakshatra": p.get("nakshatra"),
            "pada": p.get("pada"),
        })
    return out


def natal_geometric_aspects(chart):
    planets = list(chart["planets"].items())
    aspects = []
    for i in range(len(planets)):
        name_a, a = planets[i]
        for j in range(i + 1, len(planets)):
            name_b, b = planets[j]
            distance = _angular_distance(a["longitude"], b["longitude"])
            best = None
            for aspect, (angle, orb_limit) in ANGLE_ASPECTS.items():
                orb = abs(distance - angle)
                if orb <= orb_limit and (best is None or orb < best["orb"]):
                    best = {
                        "planets": [name_a, name_b],
                        "aspect": aspect,
                        "angle": angle,
                        "orb": round(orb, 2),
                        "distance": round(distance, 2),
                        "tightness": round(max(0.0, 1.0 - (orb / orb_limit)), 3),
                    }
            if best:
                aspects.append(best)
    return sorted(aspects, key=lambda x: (x["orb"], x["aspect"]))


def format_natal_evidence(chart, dasha_info=None):
    lines = ["Deterministic natal evidence:"]
    for item in natal_planet_evidence(chart):
        extra = ", ".join(item["tags"]) if item["tags"] else "no special house/motion tag"
        lines.append(
            f"  {item['planet']}: {item['sign']}, house {item['house']}, "
            f"dignity={item['dignity']}, {extra}"
        )
    aspects = natal_geometric_aspects(chart)
    if aspects:
        lines.append("Tight geometric natal aspects (comparative evidence layer):")
        for a in aspects[:12]:
            lines.append(
                f"  {a['planets'][0]} {a['aspect']} {a['planets'][1]} "
                f"(orb {a['orb']}°, tightness {a['tightness']})"
            )
    if dasha_info:
        lines.append(
            f"Timing: Mahadasha={dasha_info.get('current_mahadasha')}, "
            f"Antardasha={dasha_info.get('current_antardasha')}."
        )
    return "\n".join(lines)
