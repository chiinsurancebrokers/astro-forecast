import unittest
from datetime import date
from astro.daily_horoscope import (SIGNS, build_daily, parse_date, sky_for, solar_house)
from app import app

FAKE_SKY = dict(
    positions={'Sun': dict(sign='Scorpio', longitude=225.0, retrograde=False),
               'Moon': dict(sign='Scorpio', longitude=230.0, retrograde=False),
               'Mercury': dict(sign='Libra', longitude=200.0, retrograde=True),
               'Venus': dict(sign='Virgo', longitude=170.0, retrograde=True),
               'Mars': dict(sign='Libra', longitude=190.0, retrograde=False)},
    phase=0, elongation=5.0, aspects=[dict(body='Mercury', aspect=0, orb=0.6)])


class DailyHoroscopeTests(unittest.TestCase):
    def test_solar_houses_count_from_the_sun_sign(self):
        self.assertEqual(solar_house('Scorpio', SIGNS.index('Aries')), 8)
        self.assertEqual(solar_house('Scorpio', SIGNS.index('Scorpio')), 1)
        self.assertEqual(solar_house('Aries', SIGNS.index('Pisces')), 2)

    def test_known_sky_on_new_moon_day(self):
        sky = sky_for(date(2026, 11, 8))
        self.assertEqual(sky['positions']['Sun']['sign'], 'Scorpio')
        self.assertEqual(sky['phase'], 0)
        self.assertTrue(sky['positions']['Mercury']['retrograde'])

    def test_house_placement_and_sections_with_injected_sky(self):
        result = build_daily('Aries', date(2026, 11, 8), 'en', sky=FAKE_SKY)
        self.assertEqual(result['sky']['moon_house'], 8)
        keys = [s['key'] for s in result['sections']]
        self.assertEqual(keys, ['sky', 'general', 'love', 'work', 'mercury', 'wellbeing', 'season', 'mood', 'tip', 'prompt'])
        self.assertIn('8th house', result['sections'][1]['text'])

    def test_no_mercury_section_when_direct(self):
        sky = dict(FAKE_SKY, positions=dict(FAKE_SKY['positions'],
                   Mercury=dict(sign='Libra', longitude=200.0, retrograde=False)), aspects=[])
        keys = [s['key'] for s in build_daily('Leo', date(2026, 1, 1), 'el', sky=sky)['sections']]
        self.assertNotIn('mercury', keys)
        self.assertNotIn('mood', keys)

    def test_greek_has_no_doubled_prepositions(self):
        text = ' '.join(s['text'] for s in build_daily('Aries', date(2026, 11, 8), 'el', sky=FAKE_SKY)['sections'])
        self.assertNotIn('από στον', text)
        self.assertIn('Σκορπιό', text)

    def test_daily_card_is_the_same_for_every_sign_and_stable_per_date(self):
        first = build_daily('Aries', date(2026, 5, 1), 'en')['tarot']
        again = build_daily('Pisces', date(2026, 5, 1), 'en')['tarot']
        self.assertEqual((first['id'], first['orientation']), (again['id'], again['orientation']))
        other = {build_daily('Aries', date(2026, 5, d), 'en')['tarot']['id'] for d in range(1, 15)}
        self.assertGreater(len(other), 1)

    def test_editorial_tables_are_complete_in_both_languages(self):
        from astro import daily_texts as X
        self.assertEqual(len(X.HOUSE_TEXT), 12)
        for row in X.HOUSE_TEXT:
            self.assertEqual(len(row), 6)
            self.assertTrue(all(len(text) > 60 for text in row))
        self.assertEqual(len(X.MOON_MOOD), 12)
        self.assertEqual(len(X.PHASE_INVITE), 8)
        for pair in X.MOON_MOOD + X.PHASE_INVITE:
            self.assertTrue(pair[0] and pair[1])

    def test_every_sign_and_language_builds_all_core_sections(self):
        for lang in ('en', 'el'):
            for name in SIGNS:
                keys = [s['key'] for s in build_daily(name, date(2026, 3, 3), lang)['sections']]
                for key in ('sky', 'general', 'love', 'work', 'wellbeing', 'season', 'tip', 'prompt'):
                    self.assertIn(key, keys, (lang, name))

    def test_retrograde_venus_is_noted_and_tip_follows_the_closest_aspect(self):
        en = {s['key']: s['text'] for s in build_daily('Aries', date(2026, 11, 8), 'en', sky=FAKE_SKY)['sections']}
        self.assertIn('retrograde', en['love'])
        self.assertIn('Mars is in your 7th house', en['work'])
        self.assertIn('meets thinking and communication', en['tip'])
        el = {s['key']: s['text'] for s in build_daily('Aries', date(2026, 11, 8), 'el', sky=FAKE_SKY)['sections']}
        self.assertIn('ανάδρομη', el['love'])
        self.assertNotIn('ανάδρομος/η', el['love'])
        quiet = dict(FAKE_SKY, aspects=[])
        self.assertIn('steady rhythm', {s['key']: s['text'] for s in
                      build_daily('Aries', date(2026, 11, 8), 'en', sky=quiet)['sections']}['tip'])

    def test_parse_date_validation(self):
        self.assertEqual(parse_date('2026-11-08'), date(2026, 11, 8))
        for bad in ('2026-13-01', '08-11-2026', '1800-01-01', '2200-01-01', 'abcdefghij'):
            with self.assertRaises(ValueError):
                parse_date(bad)

    def test_routes(self):
        client = app.test_client()
        page = client.get('/horoscope?lang=en')
        self.assertEqual(page.status_code, 200)
        self.assertIn(b'Aries', page.data)
        self.assertEqual(client.get('/horoscope?lang=xx').status_code, 200)
        ok = client.get('/api/horoscope/daily?sign=Taurus&lang=en&date=2026-11-08')
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.headers['Cache-Control'], 'no-store')
        body = ok.get_json()
        self.assertEqual(body['sign'], 'Taurus')
        self.assertIn('tarot', body)
        for query in ('sign=Nope', 'sign=Aries&lang=fr', 'sign=Aries&date=2026-99-99', ''):
            self.assertEqual(client.get('/api/horoscope/daily?' + query).status_code, 400, query)


if __name__ == '__main__':
    unittest.main()
