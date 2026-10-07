"""Specialist-agent architecture for the Astrology Intelligence Engine.

These agents are deterministic evidence producers. They do not replace the
astronomical calculations and do not invent chart facts. The orchestrator merges
their outputs and keeps Vedic, Western/traditional and medical-astrology evidence
source-aware.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

from .dasha import build_mahadashas, current_period
from .forecast import monthly_forecast, house_change_calendar
from .knowledge_rules import rules_for
from .book_agent import BookKnowledgeAgent

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
OWN_SIGNS = {p: {s for s, ruler in SIGN_RULERS.items() if ruler == p} for p in set(SIGN_RULERS.values())}
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra",
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries",
}
MAJOR_ASPECTS = {
    "conjunction": (0, 8),
    "sextile": (60, 5),
    "square": (90, 7),
    "trine": (120, 7),
    "opposition": (180, 8),
}


@dataclass
class AgentResult:
    agent: str
    system: str
    evidence: list[dict[str, Any]]
    notes: list[str]
    rules: list[dict[str, Any]]

    def to_dict(self):
        return asdict(self)


def _angle_delta(a, b):
    d = abs((a - b) % 360)
    return min(d, 360 - d)


def _major_aspects(chart):
    planets = chart["planets"]
    names = list(planets)
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            delta = _angle_delta(planets[a]["longitude"], planets[b]["longitude"])
            for name, (exact, orb) in MAJOR_ASPECTS.items():
                distance = abs(delta - exact)
                if distance <= orb:
                    out.append({
                        "type": "natal_aspect",
                        "planets": [a, b],
                        "aspect": name,
                        "orb": round(distance, 2),
                        "exactness": round(max(0.0, 1 - distance / orb), 3),
                    })
                    break
    return sorted(out, key=lambda x: x["orb"])


class NatalAgent:
    name = "Natal / Genethliacal Agent"

    def run(self, chart):
        evidence = []
        asc = chart["ascendant"]
        evidence.append({
            "type": "ascendant",
            "sign": asc["sign"],
            "degree": round(asc["sign_deg"], 2),
            "ruler": SIGN_RULERS.get(asc["sign"]),
        })
        for planet, p in chart["planets"].items():
            condition = []
            if p["sign"] in OWN_SIGNS.get(planet, set()):
                condition.append("own_sign")
            if EXALTATION.get(planet) == p["sign"]:
                condition.append("exaltation")
            if DEBILITATION.get(planet) == p["sign"]:
                condition.append("debilitation")
            if p.get("retrograde"):
                condition.append("retrograde")
            evidence.append({
                "type": "planet_placement",
                "planet": planet,
                "sign": p["sign"],
                "degree": round(p["sign_deg"], 2),
                "house": p["house"],
                "nakshatra": p.get("nakshatra"),
                "pada": p.get("pada"),
                "condition": condition,
            })
        evidence.extend(_major_aspects(chart))
        return AgentResult(
            self.name,
            "MIXED_EVIDENCE",
            evidence,
            ["Natal facts remain deterministic; traditional interpretation is applied only after chart calculation."],
            rules_for("natal", "dignity", "aspects"),
        )


class TimingAgent:
    name = "Vimshottari Timing Agent"

    def run(self, birth_dt, chart, at_dt):
        periods = build_mahadashas(birth_dt, chart["planets"]["Moon"]["longitude"])
        md, ad = current_period(periods, at_dt)
        evidence = [{
            "type": "vimshottari_current",
            "at": at_dt.isoformat(),
            "mahadasha": md["lord"] if md else None,
            "mahadasha_start": md["start"].isoformat() if md else None,
            "mahadasha_end": md["end"].isoformat() if md else None,
            "antardasha": ad["lord"] if ad else None,
            "antardasha_start": ad["start"].isoformat() if ad else None,
            "antardasha_end": ad["end"].isoformat() if ad else None,
        }]
        return AgentResult(
            self.name,
            "VEDIC",
            evidence,
            ["Timing testimony should be combined with natal condition and transits rather than interpreted in isolation."],
            rules_for("timing"),
        )


class TransitAgent:
    name = "Transit Intelligence Agent"

    def run(self, chart, birth_dt, latitude, longitude, start, months):
        periods = build_mahadashas(birth_dt, chart["planets"]["Moon"]["longitude"])
        scores = monthly_forecast(chart, latitude, longitude, start, months, periods)
        changes = house_change_calendar(start, months, latitude, longitude)
        evidence = []
        for month, areas in scores.items():
            ranked = sorted(areas.items(), key=lambda kv: kv[1], reverse=True)
            evidence.append({
                "type": "monthly_activation",
                "month": month,
                "top": [{"area": a, "score": s} for a, s in ranked[:5]],
            })
        evidence.extend({"type": "slow_planet_sign_change", **ev} for ev in changes)
        return AgentResult(
            self.name,
            "VEDIC_WITH_TRADITIONAL_CORROBORATION",
            evidence,
            ["Current activation scores are still heuristic and are evidence inputs, not validated predictions."],
            rules_for("timing", "aspects"),
        )


class TraditionalKnowledgeAgent:
    name = "Traditional Knowledge Agent"

    def run(self, chart):
        topics = {"natal", "dignity", "aspects", "timing"}
        if any(p["house"] in (6, 8, 12) for p in chart["planets"].values()):
            topics.add("medical_symbolism")
        return AgentResult(
            self.name,
            "SOURCE_AWARE",
            [],
            ["Rules remain tagged by system so Western/traditional material is not silently treated as Vedic doctrine."],
            rules_for(*sorted(topics)),
        )


class MedicalAstrologyAgent:
    name = "Historical Medical Astrology Agent"

    BODY_SYMBOLISM = {
        "Sun": "vitality / heart symbolism",
        "Moon": "fluids / stomach / reproductive symbolism",
        "Mercury": "nervous-system symbolism",
        "Venus": "kidney / throat / reproductive symbolism",
        "Mars": "heat / inflammation / muscular symbolism",
        "Jupiter": "growth / liver symbolism",
        "Saturn": "restriction / bones / chronicity symbolism",
    }

    def run(self, chart):
        evidence = []
        for planet, p in chart["planets"].items():
            if planet in self.BODY_SYMBOLISM and p["house"] in (1, 6, 8, 12):
                evidence.append({
                    "type": "historical_medical_symbolism",
                    "planet": planet,
                    "house": p["house"],
                    "sign": p["sign"],
                    "symbolic_correspondence": self.BODY_SYMBOLISM[planet],
                })
        return AgentResult(
            self.name,
            "MEDICAL_ASTROLOGY_HISTORICAL_ONLY",
            evidence,
            [
                "Not medical advice.",
                "Do not infer disease, diagnosis, prognosis, treatment, or clinical risk from these symbolic correspondences.",
            ],
            rules_for("planetary_strength", "medical_symbolism", "safety", systems={"MEDICAL_ASTROLOGY"}),
        )


class CalibrationAgent:
    name = "Calibration Agent"

    def run(self, outcomes=None):
        outcomes = outcomes or []
        evidence = [{"type": "logged_outcome", **o} for o in outcomes if isinstance(o, dict)]
        return AgentResult(
            self.name,
            "EMPIRICAL_CALIBRATION",
            evidence,
            ["No personal predictive calibration is claimed until enough dated real-world outcomes have been logged."],
            [],
        )


class SynthesisAgent:
    name = "Synthesis Agent"

    def run(self, specialist_results, question=""):
        agent_names = [r.agent for r in specialist_results]
        return AgentResult(
            self.name,
            "ORCHESTRATION",
            [{
                "type": "synthesis_plan",
                "question": question,
                "agents_used": agent_names,
                "principle": "Calculated facts first; source-aware rules second; prose synthesis last.",
            }],
            [
                "Vedic and Western/traditional rules must remain distinguishable in the final narrative.",
                "Medical-astrology material must always be labelled historical/symbolic.",
            ],
            [],
        )


class AstrologyOrchestrator:
    """Run specialist agents and return one inspectable evidence bundle."""

    def __init__(self):
        self.natal = NatalAgent()
        self.timing = TimingAgent()
        self.transit = TransitAgent()
        self.knowledge = TraditionalKnowledgeAgent()
        self.book_knowledge = BookKnowledgeAgent()
        self.medical = MedicalAstrologyAgent()
        self.calibration = CalibrationAgent()
        self.synthesis = SynthesisAgent()

    def run(self, chart, birth_dt, latitude, longitude, start, months=24,
            question="", outcomes=None, at_dt=None, second_chart=None, geo_location=None, utc_offset=0):
        at_dt = at_dt or datetime.now()
        from .specialist_agents import (
            AskAgent, CareerAgent, CompatibilityAgent, GeoAstrologyAgent,
            PredictiveTimingEnsemble,
        )

        natal_result = self.natal.run(chart)
        timing_result = self.timing.run(birth_dt, chart, at_dt)
        transit_result = self.transit.run(
            chart, birth_dt, latitude, longitude, start, months,
        )
        specialists = [
            natal_result,
            timing_result,
            transit_result,
            self.knowledge.run(chart),
            self.medical.run(chart),
            self.calibration.run(outcomes),
            CareerAgent().run(chart),
        ]
        monthly_scores = {
            item["month"]: {
                signal["area"]: signal["score"] for signal in item.get("top", [])
            }
            for item in transit_result.evidence
            if item.get("type") == "monthly_activation"
        }
        transit_events = [
            item for item in transit_result.evidence
            if item.get("type") == "slow_planet_sign_change"
        ]
        specialists.append(PredictiveTimingEnsemble().run(
            monthly_scores, timing_result.evidence, transit_events, outcomes,
        ))
        if question:
            specialists.append(AskAgent().run(
                question,
                ["Natal / Genethliacal Agent", "Vimshottari Timing Agent",
                 "Transit Intelligence Agent", "Career Agent",
                 "Compatibility Agent", "GeoAstrology Agent"],
            ))
        if second_chart is not None:
            specialists.append(CompatibilityAgent().run(chart, second_chart))
        if geo_location is not None:
            from .ephemeris import build_natal_chart
            geo_birth = {
                "year": birth_dt.year, "month": birth_dt.month, "day": birth_dt.day,
                "hour": birth_dt.hour, "minute": birth_dt.minute,
                "utc_offset": utc_offset, "chart": chart,
            }
            specialists.append(GeoAstrologyAgent().run(
                geo_birth, geo_location["latitude"], geo_location["longitude"],
                build_natal_chart,
            ))
        book_library = self.book_knowledge.run(
            question=question,
            chart=chart,
            life_areas=["career", "money", "marriage", "travel"],
            timing=True,
            include_medical=True,
            limit=16,
        )
        specialists.append(self.synthesis.run(specialists, question))
        return {
            "architecture": "Astrology Intelligence Engine v2",
            "agent_count": len(specialists),
            "agents": [r.to_dict() for r in specialists],
            "book_knowledge": book_library,
            "guardrails": {
                "medical_astrology": "historical/symbolic only; not diagnosis or medical advice",
                "forecasting": "heuristic evidence is not validated prediction",
                "systems": "Vedic, Western/traditional and medical-astrology rules stay source-tagged",
            },
        }
