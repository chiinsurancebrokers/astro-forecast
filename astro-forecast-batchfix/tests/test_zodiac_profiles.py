import unittest
from astro.zodiac_profiles import build_zodiac_profile
from astro.natal_books import SUN_READINGS, citation, build_book_natal_report
from astro.ephemeris import build_natal_chart
from app import app

class ZodiacProfileTests(unittest.TestCase):
    def test_all_twelve_have_substantial_distinct_source_portraits(self):
        from astro.bart_profiles import BART_PROFILES
        self.assertEqual(set(BART_PROFILES), set(SUN_READINGS))
        bodies=[]
        for sign in SUN_READINGS:
            profile=build_zodiac_profile(sign,SUN_READINGS,citation)
            body=' '.join(p for section in profile['sections'] for p in section['paragraphs'])
            self.assertGreater(len(body.split()),240)
            self.assertNotIn('Which ',body)
            self.assertEqual(profile['references'][0]['source_id'],'bart_success')
            self.assertIn('1923–1930',profile['method'])
            self.assertTrue(any(s['title']=='Relationships and belonging' for s in profile['sections']))
            self.assertTrue(any(s['title']=='Work, ambition and contribution' for s in profile['sections']))
            bodies.append(body)
        self.assertEqual(len(set(bodies)),12)

    def test_aquarius_uses_its_checked_bart_and_karma_passages(self):
        profile=build_zodiac_profile('Aquarius',SUN_READINGS,citation)
        refs=profile['references']
        self.assertEqual([r['pdf_page'] for r in refs if r['source_id']=='bart_success'],[100,101,102,103])
        self.assertEqual([r['printed_page'] for r in refs if r['source_id']=='bart_success'],[92,93,94,95])
        self.assertEqual([r['pdf_page'] for r in refs if r['source_id']=='karma_ancient_egyptians'],[71,72])
        body=' '.join(p for s in profile['sections'] for p in s['paragraphs'])
        self.assertIn('rebuilding after disruption',body)
        self.assertIn('social circle',body)
        self.assertNotIn('1975',body)
        self.assertNotIn('millionaire',body)

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
