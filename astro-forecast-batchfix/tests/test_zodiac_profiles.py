import unittest
from astro.zodiac_profiles import build_zodiac_profile, PROMPTS
from astro.natal_books import SUN_READINGS, citation, build_book_natal_report
from astro.ephemeris import build_natal_chart
from app import app

class ZodiacProfileTests(unittest.TestCase):
    def test_all_twelve_have_verified_source_and_editorial_roles(self):
        self.assertEqual(set(PROMPTS),set(SUN_READINGS))
        for index,sign in enumerate(SUN_READINGS):
            p=build_zodiac_profile(sign,SUN_READINGS,citation)
            self.assertEqual(p['sections'][0]['paragraphs'],[SUN_READINGS[sign]])
            self.assertEqual(p['references'][0]['pdf_page'],index+8)
            self.assertEqual(p['sections'][0]['role'],'verified_paraphrase')
            self.assertTrue(all(s['role']=='editorial_application' for s in p['sections'][1:]))
            self.assertIn('does not calculate event dates',p['method'])

    def test_catalog_and_validation(self):
        client=app.test_client()
        self.assertEqual(len(client.get('/api/zodiac/profiles').json['profiles']),12)
        self.assertEqual(client.get('/api/zodiac/profiles?sign=invalid').status_code,400)
        response=client.get('/api/zodiac/profiles?sign=Aquarius')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['zodiac_profile']['sign'],'Aquarius')

    def test_natal_uses_calculated_tropical_sun(self):
        chart=build_natal_chart(1975,2,8,11,20,2,37.9838,23.7275)
        report=build_book_natal_report(chart,37.9838,23.7275)
        self.assertEqual(report['zodiac_profile']['sign'],report['planets']['Sun']['sign'])
        self.assertEqual(report['zodiac_profile']['sign'],'Aquarius')

if __name__=='__main__': unittest.main()
