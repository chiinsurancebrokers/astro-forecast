import unittest

from app import app


class SpecialistRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_ask_requires_question(self):
        response = self.client.get("/api/agents/ask")
        self.assertEqual(response.status_code, 400)

    def test_compatibility_requires_second_chart_date(self):
        response = self.client.get("/api/agents/compatibility")
        self.assertEqual(response.status_code, 400)

    def test_geo_requires_coordinates(self):
        response = self.client.get("/api/agents/geo")
        self.assertEqual(response.status_code, 400)

    def test_orchestrator_includes_timing_career_and_ask_agents(self):
        response = self.client.get(
            "/api/agents/analyze?year=1990&month=5&day=12&hour=12&minute=0"
            "&utc_offset=0&latitude=37.98&longitude=23.72&months=1"
            "&start=2026-10-01&question=career%20timing"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        names = {agent["agent"] for agent in payload["agents"]}
        self.assertIn("Career Agent", names)
        self.assertIn("Multi-model Predictive Timing Agent", names)
        self.assertIn("Ask Agent", names)
        timing = next(a for a in payload["agents"]
                      if a["agent"] == "Multi-model Predictive Timing Agent")
        self.assertIn("not a probability", " ".join(timing["notes"]).lower())


if __name__ == "__main__":
    unittest.main()
