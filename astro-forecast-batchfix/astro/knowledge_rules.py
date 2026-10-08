"""Source-aware traditional astrology rule registry.

The registry deliberately stores compact paraphrased rules rather than book text.
Each rule carries a system tag and provenance label so Vedic, Western/traditional,
and medical-astrology material is not silently blended.

The sources are the user-supplied historical astrology books reviewed for this
project. Medical-astrology material is historical/symbolic only and must never be
presented as diagnosis, prognosis, treatment, or a substitute for medical care.
"""

RULES = [
    {
        "id": "traditional.aspects.exactness",
        "system": "WESTERN_TRADITIONAL",
        "topic": "aspects",
        "summary": "Aspect influence is treated as stronger when the angular distance is closer to exact.",
        "source": "Astrology of the Ancient Egyptians — Planetary Aspects",
    },
    {
        "id": "traditional.dignity.sign_rulership",
        "system": "WESTERN_TRADITIONAL",
        "topic": "dignity",
        "summary": "Planetary condition depends materially on sign rulership, exaltation, fall and related dignity concepts.",
        "source": "The Guide to Astrology — Essential and Accidental Dignities",
    },
    {
        "id": "traditional.transit.confirmation",
        "system": "WESTERN_TRADITIONAL",
        "topic": "timing",
        "summary": "A transit should not be treated as sufficient on its own; converging timing testimony increases interpretive weight.",
        "source": "The Guide to Astrology — Transits and Eclipses",
    },
    {
        "id": "traditional.transit.houses",
        "system": "WESTERN_TRADITIONAL",
        "topic": "timing",
        "summary": "Transits through natal houses are treated as important timing testimony and should be interpreted in the context of the radix.",
        "source": "The Guide to Astrology — Transits and Eclipses",
    },
    {
        "id": "traditional.radix.sequence",
        "system": "WESTERN_TRADITIONAL",
        "topic": "natal",
        "summary": "Judgment proceeds from signs, rulers, planetary motion, houses, aspects, exaltation/fall and planet-in-sign meanings before synthesis of the radix.",
        "source": "A Guide To Astrology — Lessons in Astrology",
    },
    {
        "id": "medical.strength.multifactor",
        "system": "MEDICAL_ASTROLOGY",
        "topic": "planetary_strength",
        "summary": "Planetary strength is multi-factorial: aspect, position, natural, motional, directional and temporal strength are distinct considerations.",
        "source": "Medical Astrology — Gauging Planetary Strength in the Specific Horoscope",
    },
    {
        "id": "medical.combination.context",
        "system": "MEDICAL_ASTROLOGY",
        "topic": "medical_symbolism",
        "summary": "Historical medical-astrology judgment depends on combinations of planet, sign, aspect and house; isolated correspondences are not sufficient.",
        "source": "Medical Astrology — Zodiaco-Planetary Synopsis / planetary combinations",
    },
    {
        "id": "medical.guardrail",
        "system": "MEDICAL_ASTROLOGY",
        "topic": "safety",
        "summary": "Medical-astrology outputs are historical symbolic interpretations only, never diagnosis, prognosis or treatment advice.",
        "source": "Application guardrail for this project",
    },
]

BY_TOPIC = {}
for _rule in RULES:
    BY_TOPIC.setdefault(_rule["topic"], []).append(_rule)


def rules_for(*topics, systems=None):
    """Return compact rule records filtered by topic/system."""
    wanted = set(topics)
    out = [r for r in RULES if not wanted or r["topic"] in wanted]
    if systems:
        allowed = set(systems)
        out = [r for r in out if r["system"] in allowed]
    return out
