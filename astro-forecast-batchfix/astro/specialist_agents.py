"""Specialist analysis agents for compatibility, career, relocation, and questions.

All outputs are evidence summaries grounded in computed chart placements. Scores
are descriptive indices, not validated outcomes or deterministic life claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
MAJOR_ASPECTS = {
    "conjunction": (0, 8), "sextile": (60, 5), "square": (90, 7),
    "trine": (120, 7), "opposition": (180, 8),
}


def _angle_delta(a, b):
    delta = abs((a - b) % 360)
    return min(delta, 360 - delta)


@dataclass
class SpecialistReport:
    agent: str
    system: str
    evidence: list[dict[str, Any]]
    notes: list[str]

    def to_dict(self):
        return asdict(self)


def _aspect_between(a: float, b: float):
    delta = _angle_delta(a, b)
    for name, (exact, orb) in MAJOR_ASPECTS.items():
        distance = abs(delta - exact)
        if distance <= orb:
            return {"aspect": name, "orb": round(distance, 2)}
    return None


class CompatibilityAgent:
    """Pairwise synastry evidence across luminaries, personal planets and angles."""

    name = "Compatibility Agent"

    def run(self, chart_a, chart_b):
        evidence = []
        a_planets, b_planets = chart_a["planets"], chart_b["planets"]
        pairs = [("Sun", "Sun"), ("Moon", "Moon"), ("Sun", "Moon"),
                 ("Moon", "Sun"), ("Venus", "Mars"), ("Mars", "Venus"),
                 ("Mercury", "Mercury"), ("Venus", "Venus")]
        for left, right in pairs:
            aspect = _aspect_between(a_planets[left]["longitude"], b_planets[right]["longitude"])
            if aspect:
                evidence.append({"type": "cross_chart_aspect", "a": left,
                                 "b": right, **aspect})
        for planet in ("Sun", "Moon", "Mercury", "Venus", "Mars"):
            evidence.append({
                "type": "placement_pair",
                "planet": planet,
                "person_a": a_planets[planet]["sign"],
                "person_b": b_planets[planet]["sign"],
            })
        return SpecialistReport(
            self.name, "VEDIC_SIDEREAL_SYNASTRY", evidence,
            ["This is a comparison of selected chart factors, not a relationship outcome prediction.",
             "Birth-time uncertainty can materially change houses and angles."],
        )


class CareerAgent:
    """Summarize career-related natal factors without declaring an occupation."""

    name = "Career Agent"
    CAREER_HOUSES = (2, 6, 10, 11)

    def run(self, chart):
        evidence = []
        asc_ruler = SIGN_RULERS.get(chart["ascendant"]["sign"])
        for planet, placement in chart["planets"].items():
            if placement["house"] in self.CAREER_HOUSES:
                evidence.append({
                    "type": "career_house_placement",
                    "planet": planet,
                    "house": placement["house"],
                    "sign": placement["sign"],
                    "retrograde": bool(placement.get("retrograde", False)),
                })
        if asc_ruler in chart["planets"]:
            ruler = chart["planets"][asc_ruler]
            evidence.append({
                "type": "ascendant_ruler",
                "planet": asc_ruler,
                "house": ruler["house"],
                "sign": ruler["sign"],
            })
        evidence.sort(key=lambda item: (item.get("house", 0), item.get("planet", "")))
        return SpecialistReport(
            self.name, "VEDIC_NATAL_EVIDENCE", evidence,
            ["Use as reflective themes; this does not identify a guaranteed career or financial result."],
        )


class GeoAstrologyAgent:
    """Compare natal and relocated angles using the existing chart calculator."""

    name = "GeoAstrology Agent"

    def run(self, birth, latitude, longitude, build_chart):
        relocated = build_chart(
            birth["year"], birth["month"], birth["day"], birth["hour"],
            birth["minute"], birth["utc_offset"], latitude, longitude,
        )
        evidence = [{
            "type": "relocated_ascendant",
            "natal_sign": birth["chart"]["ascendant"]["sign"],
            "relocated_sign": relocated["ascendant"]["sign"],
            "relocated_degree": round(relocated["ascendant"]["sign_deg"], 2),
            "coordinates": {"latitude": latitude, "longitude": longitude},
        }]
        for planet, placement in relocated["planets"].items():
            natal = birth["chart"]["planets"][planet]
            if placement["house"] != natal["house"]:
                evidence.append({
                    "type": "relocated_house_change", "planet": planet,
                    "natal_house": natal["house"], "relocated_house": placement["house"],
                    "sign": placement["sign"],
                })
        return SpecialistReport(
            self.name, "VEDIC_RELOCATION_COMPARISON", evidence,
            ["This compares whole-sign house emphasis at the supplied coordinates; it does not calculate astrocartography line crossings or recommend a destination."],
        )


class AskAgent:
    """Route a natural-language question to relevant evidence domains."""

    name = "Ask Agent"
    ROUTES = {
        "career": ("career", "job", "work", "profession", "business"),
        "compatibility": ("relationship", "partner", "compatib", "marriage", "love"),
        "timing": ("when", "timing", "period", "month", "year", "transit"),
        "geoastrology": ("relocat", "move", "travel", "location", "city"),
    }

    def run(self, question: str, available_agents: list[str]):
        normalized = question.casefold().strip()
        routes = [domain for domain, terms in self.ROUTES.items()
                  if any(term in normalized for term in terms)]
        if not routes:
            routes = ["natal", "timing"]
        return SpecialistReport(
            self.name, "QUESTION_ROUTING",
            [{"type": "question_intent", "question": question,
              "domains": routes, "available_agents": available_agents}],
            ["Question routing selects evidence domains; it does not supply an answer unsupported by computed evidence."],
        )


class PredictiveTimingEnsemble:
    """Combine timing evidence streams transparently, without claiming validation."""

    name = "Multi-model Predictive Timing Agent"

    def run(self, monthly_scores, dasha_evidence, transit_events, outcomes=None):
        outcomes = outcomes or []
        evidence = [{
            "type": "timing_model_coverage",
            "models": [
                {"name": "transit_activation", "available": bool(monthly_scores),
                 "validated": False},
                {"name": "vimshottari_periods", "available": bool(dasha_evidence),
                 "validated": False},
                {"name": "ingressed_transits", "available": bool(transit_events),
                 "validated": False},
                {"name": "outcome_calibration", "available": len(outcomes) >= 30,
                 "sample_size": len(outcomes), "validated": False},
            ],
        }]
        if monthly_scores:
            evidence.extend({
                "type": "timing_window",
                "month": month,
                "signals": [{"area": area, "score": score}
                            for area, score in sorted(scores.items(),
                                                      key=lambda item: item[1], reverse=True)[:3]],
                "method": "heuristic transit activation",
            } for month, scores in monthly_scores.items())
        return SpecialistReport(
            self.name, "UNCALIBRATED_EVIDENCE_ENSEMBLE", evidence,
            ["Timing evidence streams are shown side by side; no probability or validated prediction is inferred.",
             "Outcome calibration becomes available only after a sufficiently large, dated, consented outcome dataset is collected."],
        )
