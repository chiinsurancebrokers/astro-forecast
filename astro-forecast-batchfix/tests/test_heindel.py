import unittest
from datetime import date
from astro.additional_books import heindel_sections, HEINDEL_HOUSE
from astro.daily_horoscope import build_daily
from astro.natal_books import citation


class HeindelTests(unittest.TestCase):
    def planets(self, signs):
        return {n: {'sign': s, 'house': i + 1} for i, (n, s) in enumerate(zip(
            ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'], signs))}

    def test_dominant_quality_and_citation(self):
        p = self.planets(['Aries', 'Cancer', 'Libra', 'Capricorn', 'Taurus', 'Gemini', 'Aries'])
        s = heindel_sections(p, citation)
        self.assertIn('5 of 7 are in Cardinal', s[0]['paragraphs'][0])
        self.assertEqual((s[0]['citations'][0]['printed_page'], s[0]['citations'][0]['pdf_page']), (100, 108))
        self.assertEqual(s[0]['citations'][0]['source_id'], 'heindel_simplified')

    def test_tie_is_not_called_a_lean(self):
        p = self.planets(['Aries', 'Cancer', 'Taurus', 'Leo', 'Gemini', 'Virgo', 'Libra'])
        self.assertNotIn(' of 7 are in', heindel_sections(p, citation)[0]['paragraphs'][0])

    def test_houses_only_when_known_and_no_predictions(self):
        p = self.planets(['Aries'] * 7)
        for v in p.values():
            v.pop('house')
        titles = [s['title'] for s in heindel_sections(p, citation)]
        self.assertNotIn('Heindel · where your personal planets sit', titles)
        self.assertEqual(len(HEINDEL_HOUSE), 12)

    def test_daily_mentions_quality_and_source(self):
        for lang in ('el', 'en'):
            r = build_daily('Leo', date(2026, 11, 8), lang)
            general = next(s['text'] for s in r['sections'] if s['key'] == 'general')
            self.assertIn('Heindel', general)
            self.assertIn('Heindel', r['method'])


if __name__ == '__main__':
    unittest.main()
