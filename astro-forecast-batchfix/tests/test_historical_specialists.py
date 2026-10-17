import unittest
import swisseph as swe
from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.historical_specialists import run_historical_specialists, plan_catalogue


class HistoricalSpecialistTests(unittest.TestCase):
    def test_heliocentric_evidence_and_source_scope(self):
        init_ephemeris()
        chart = build_natal_chart(1975, 2, 8, 11, 20, 2, 37.9838, 23.7275)
        reports = run_historical_specialists(chart)
        self.assertEqual([r['id'] for r in reports], ['merton', 'daath', 'raleigh'])
        earth = reports[0]['evidence']['Earth']['longitude']
        sun, _ = swe.calc_ut(chart['julian_day'], swe.SUN, swe.FLG_MOSEPH)
        self.assertAlmostEqual((earth - sun[0]) % 360, 180, places=3)
        self.assertEqual(len(reports[0]['evidence']), 6)
        self.assertIsNone(reports[1]['evidence']['formal_strength_score'])
        self.assertIsNone(reports[2]['evidence']['personal_numeric_score'])
        for report in reports:
            self.assertTrue(report['paragraphs'])
            self.assertTrue(report['scope'])
            self.assertTrue(all(ref['pdf_page'] > 0 and ref['kind'] == 'verified_paraphrase' for ref in report['references']))

    def test_preview_does_not_claim_active_billing(self):
        plans = plan_catalogue()
        self.assertFalse(plans['billing_active'])
        self.assertEqual([p['id'] for p in plans['plans']], ['free', 'plus'])
        self.assertEqual(plans['plans'][0]['price'], 0)
        self.assertIsNone(plans['plans'][1]['price'])
