import unittest

from astro.specialist_agents import (
    AskAgent,
    CareerAgent,
    CompatibilityAgent,
    GeoAstrologyAgent,
    PredictiveTimingEnsemble,
)


def chart(asc="Aries", offset=0):
    planets = {}
    names = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
             "Rahu", "Ketu")
    signs = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
             "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
    for i, name in enumerate(names):
        longitude = (i * 37 + offset) % 360
        sign_index = int(longitude // 30)
        planets[name] = {
            "longitude": longitude,
            "sign": signs[sign_index],
            "house": (i % 12) + 1,
            "retrograde": False,
        }
    return {"ascendant": {"sign": asc, "sign_deg": 4.0}, "planets": planets}


class SpecialistAgentTests(unittest.TestCase):
    def test_compatibility_reports_cross_chart_evidence(self):
        report = CompatibilityAgent().run(chart(), chart(offset=5)).to_dict()
        self.assertEqual(report["agent"], "Compatibility Agent")
        self.assertTrue(any(x["type"] == "placement_pair" for x in report["evidence"]))
        self.assertTrue(any(x["type"] == "cross_chart_aspect" for x in report["evidence"]))

    def test_career_limits_evidence_to_career_houses_and_ruler(self):
        report = CareerAgent().run(chart()).to_dict()
        self.assertTrue(any(x["type"] == "ascendant_ruler" for x in report["evidence"]))
        for item in report["evidence"]:
            if item["type"] == "career_house_placement":
                self.assertIn(item["house"], (2, 6, 10, 11))

    def test_geo_compares_relocated_chart(self):
        calls = []
        def build(*args):
            calls.append(args)
            return chart(asc="Taurus", offset=20)
        natal = chart()
        report = GeoAstrologyAgent().run(
            {"chart": natal, "year": 1980, "month": 1, "day": 2, "hour": 3,
             "minute": 4, "utc_offset": 0},
            51.5, -0.1, build,
        ).to_dict()
        self.assertEqual(len(calls), 1)
        self.assertEqual(report["evidence"][0]["relocated_sign"], "Taurus")

    def test_ask_routes_question_to_relevant_domain(self):
        report = AskAgent().run("When is a good career timing?", ["Career Agent"]).to_dict()
        self.assertIn("career", report["evidence"][0]["domains"])
        self.assertIn("timing", report["evidence"][0]["domains"])

    def test_timing_ensemble_discloses_unvalidated_models(self):
        report = PredictiveTimingEnsemble().run(
            {"2026-01": {"career": 62}}, [{"type": "dasha"}], [], outcomes=[]
        ).to_dict()
        coverage = report["evidence"][0]["models"]
        self.assertTrue(all(item["validated"] is False for item in coverage))
        self.assertFalse(coverage[0]["available"] is False)
        self.assertTrue(any(item["type"] == "timing_window" for item in report["evidence"]))


if __name__ == "__main__":
    unittest.main()
