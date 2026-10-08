import unittest
import swisseph as swe
from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.natal_books import build_book_natal_report
from astro.western_delineation import SIGN_TRAITS, SIGNS, essential_condition


class WesternDelineationTests(unittest.TestCase):
    def test_complete_planet_and_house_coverage_matches_evidence(self):
        init_ephemeris()
        chart = build_natal_chart(1975, 2, 8, 11, 20, 2, 37.9838, 23.7275)
        report = build_book_natal_report(chart,37.9838,23.7275)
        reading = report['reading']
        self.assertEqual(len(reading['planet_sections']),9)
        self.assertEqual([s['house'] for s in reading['house_sections']],list(range(1,13)))
        for section in reading['planet_sections']:
            self.assertEqual(section['evidence']['house'],report['planets'][section['planet']]['house'])
            self.assertTrue(section['citations'])
        assigned = [p for h in reading['house_sections'] for p in h['occupants']]
        self.assertEqual(sorted(assigned),sorted(report['planets']))
        for h in reading['house_sections']:
            self.assertEqual(h['ruler_house'],report['planets'][h['ruler']]['house'])
            self.assertTrue(h['paragraphs'])
        self.assertEqual(report['planets']['Sun']['house'],10)
        self.assertEqual(next(s for s in reading['planet_sections'] if s['planet']=='Sun')['evidence']['essential_condition'],['detriment'])
        self.assertTrue(any(c['pdf_page']==63 and c['source_id']=='raphael_guide' for c in reading['references']))
        self.assertTrue(any(c['pdf_page']==45 and c['source_id']=='white_guide' for c in reading['references']))
        keys = [(c['source_id'],c['pdf_page'],c['chapter']) for c in reading['references']]
        self.assertEqual(len(keys),len(set(keys)))

    def test_no_location_does_not_invent_house_analysis(self):
        report = build_book_natal_report({'julian_day':2451545.0})
        self.assertEqual(report['reading']['house_sections'],[])
        self.assertEqual(len(report['reading']['planet_sections']),9)
        self.assertTrue(all('house' not in s['evidence'] for s in report['reading']['planet_sections']))

    def test_rulership_and_dignity_are_named_without_fake_scores(self):
        self.assertEqual(essential_condition('Venus','Pisces'),['exaltation'])
        self.assertEqual(essential_condition('Mars','Capricorn'),['exaltation'])
        self.assertEqual(essential_condition('Jupiter','Pisces'),['domicile'])
        self.assertEqual(essential_condition('Saturn','Cancer'),['detriment'])
        self.assertEqual(essential_condition('Neptune','Pisces'),[])
        for traits in SIGN_TRAITS.values():
            self.assertEqual(len(traits),len(SIGNS))
            self.assertTrue(all(37 <= page <= 45 for _,page in traits))
