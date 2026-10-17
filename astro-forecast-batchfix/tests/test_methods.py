import unittest
from concurrent.futures import ThreadPoolExecutor
import swisseph as swe
from app import app


class MethodsTests(unittest.TestCase):
    def test_coordinate_difference_and_no_probability(self):
        response = app.test_client().get('/api/agents/methods?at=2026-10-17T12:00:00Z')
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        ayan = body['calculation']['birth_ayanamsha_degrees']
        for row in body['natal_comparison']:
            difference = (row['western']['longitude'] - row['vedic']['longitude']) % 360
            self.assertAlmostEqual(difference, ayan, delta=.01)
        self.assertNotIn('probability', body)
        self.assertEqual(body['vedic']['ayanamsha'], 'Lahiri')
        self.assertEqual(body['western']['zodiac'], 'tropical')

    def test_sidereal_mode_is_reset_in_worker_threads(self):
        def compute(_):
            swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
            data = app.test_client().get('/api/agents/methods?at=2026-10-17T12:00:00Z').get_json()
            return data['natal_comparison'][0]['vedic']['longitude']
        with ThreadPoolExecutor(max_workers=4) as pool:
            values = list(pool.map(compute, range(8)))
        self.assertLess(max(values) - min(values), 1e-8)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        from astro.ephemeris import build_natal_chart
        expected = build_natal_chart(1975,2,8,11,20,2,37.9838,23.7275)
        self.assertAlmostEqual(values[0], expected['planets']['Sun']['longitude'])

    def test_invalid_inputs_and_naive_time_are_rejected(self):
        for query in ('latitude=nan','latitude=91','utc_offset=15','month=13',
                      'at=2026-10-17T12:00:00','at=bad'):
            self.assertEqual(app.test_client().get('/api/agents/methods?'+query).status_code,400,query)

    def test_same_instant_in_different_timezones(self):
        client = app.test_client()
        a = client.get('/api/agents/methods',query_string={'at':'2026-10-17T12:00:00Z'}).get_json()
        b = client.get('/api/agents/methods',query_string={'at':'2026-10-17T15:00:00+03:00'}).get_json()
        self.assertEqual(a['western']['transits'],b['western']['transits'])
        self.assertEqual(a['vedic'],b['vedic'])

    def test_methods_page_and_platform_link(self):
        client=app.test_client()
        self.assertEqual(client.get('/methods').status_code,200)
        self.assertIn(b'href="/methods"',client.get('/platform').data)

    def test_logged_outcome_count_does_not_claim_calibration(self):
        from astro.specialist_agents import PredictiveTimingEnsemble
        report=PredictiveTimingEnsemble().run({},[],[],[{'result':'match'}]*100)
        coverage=report.evidence[0]['models'][-1]
        self.assertTrue(coverage['logged_outcomes_available'])
        self.assertFalse(coverage['available'])
        self.assertFalse(coverage['validated'])


if __name__ == '__main__':
    unittest.main()
