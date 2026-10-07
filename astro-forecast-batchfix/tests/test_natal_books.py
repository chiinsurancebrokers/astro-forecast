import unittest
from copy import deepcopy
from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.natal_books import build_book_natal_report, SUN_READINGS


class BookNatalTests(unittest.TestCase):
    def test_tropical_report_keeps_lahiri_distinct(self):
        init_ephemeris()
        chart = build_natal_chart(1975, 2, 8, 11, 20, 2, 37.9838, 23.7275)
        before = deepcopy(chart)
        report = build_book_natal_report(chart, 37.9838, 23.7275)
        self.assertEqual(chart, before)
        self.assertEqual(chart['planets']['Sun']['sign'], 'Capricorn')
        self.assertEqual(report['chart']['planets']['Sun']['sign'], 'Aquarius')
        self.assertEqual(report['sections'][0]['citations'][0]['pdf_page'], 18)
        self.assertEqual(report['chart']['ascendant']['sign'], 'Taurus')
        for section in report['sections']:
            self.assertTrue(section['citations'])
            self.assertTrue(all(c['kind'] == 'verified_paraphrase' for c in section['citations']))
        self.assertEqual(set(SUN_READINGS), set(['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']))

    def test_missing_location_does_not_invent_houses(self):
        report = build_book_natal_report({'julian_day':2451545.0})
        self.assertIsNone(report['chart'])
        self.assertNotIn('house', report['planets']['Moon'])
