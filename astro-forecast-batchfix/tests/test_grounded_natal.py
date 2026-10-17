from copy import deepcopy
import math
import unittest
from unittest.mock import patch
from app import app
from astro.ephemeris import init_ephemeris,build_natal_chart
from astro.natal_books import build_book_natal_report
from astro.grounded_natal import build_reader_edition,check_plugin_records,AUTHOR_PATTERN


class GroundedNatalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_ephemeris()
        cls.report=build_book_natal_report(build_natal_chart(1975,2,8,11,20,2,37.9838,23.7275),37.9838,23.7275)

    def test_complete_reader_coverage_and_sources_only_at_end(self):
        r=self.report['reader_edition']
        self.assertEqual(len(r['planet_sections']),9)
        self.assertEqual(len(r['house_sections']),12)
        self.assertFalse(r['excluded'])
        for group in ('sections','planet_sections','house_sections'):
            for item in r[group]:
                self.assertNotIn('citations',item)
                self.assertFalse(any(AUTHOR_PATTERN.search(p) for p in item['paragraphs']))
                trace=next(a for a in r['audit'] if a['section_id']==item['section_id'])
                self.assertTrue(trace['sources'])
                self.assertTrue(trace['facts'] or trace['kind']=='editorial_reflection_not_a_chart_claim')
        self.assertTrue(r['references'])

    def test_invented_prose_with_real_citation_is_excluded(self):
        report=deepcopy(self.report)
        report['reading']['sections'][0]['paragraphs'].append('You will certainly marry in 2027.')
        r=build_reader_edition(report)
        self.assertTrue(any(i['section_id']=='sections:0' for i in r['excluded']))
        self.assertNotIn('certainly marry',str(r['sections']))

    def test_fake_aspect_and_fake_source_page_are_excluded(self):
        report=deepcopy(self.report)
        section=next(s for s in report['reading']['sections'] if 'evidence' in s)
        section['evidence']['orb']=4.99
        report['reading']['planet_sections'][0]['citations'][0]['pdf_page']=999
        r=build_reader_edition(report)
        self.assertGreaterEqual(len(r['excluded']),2)
        self.assertFalse(any(ref['pdf_page']==999 for ref in r['references']))

    def test_wrong_house_and_plausible_but_wrong_longitude_fail(self):
        report=deepcopy(self.report)
        report['chart']['planets']['Sun']['house']=2
        with self.assertRaises(ValueError):build_reader_edition(report)
        report=deepcopy(self.report)
        report['chart']['planets']['Sun']['longitude']+=.1
        report['chart']['planets']['Sun']['sign_deg']+=.1
        with self.assertRaises(ValueError):build_reader_edition(report)

    def test_compatible_plugin_positions_only_and_fail_closed(self):
        chart=self.report['chart']
        good={'provider':'internal_test_fixture','zodiac':'tropical','house_system':'whole_sign',
              'time_basis':'UTC','julian_day':chart['julian_day'],'coordinates':chart['coordinates'],
              'planets':{'Sun':chart['planets']['Sun']['longitude']},'prose':'You are destined for fame.'}
        result=check_plugin_records([good],chart)
        self.assertEqual(result['records'][0]['status'],'numerical_crosscheck_only')
        self.assertNotIn('destined',str(result))
        for change in ({'zodiac':'sidereal'},{'julian_day':float('nan')},
                       {'planets':{'Sun':'Aquarius'}},{'planets':{'Sun':0}},
                       {'coordinates':None},{'time_basis':None}):
            result=check_plugin_records([{**good,**change}],chart)
            self.assertEqual(result['records'][0]['status'],'excluded',change)
        self.assertEqual(check_plugin_records([],chart)['status'],'not_connected')

    def test_printable_report_validation_and_source_placement(self):
        client=app.test_client()
        self.assertEqual(client.post('/natal-reading',data={}).status_code,400)
        values=dict(year=1975,month=2,day=8,hour=11,minute=20,utc_offset=2,
                    latitude=37.9838,longitude=23.7275,time_quality='approximate')
        response=client.post('/natal-reading',data=values)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        text=response.get_data(as_text=True)
        narrative=text.split('<div id="natal-narrative">')[1].split('<section><h2>Calculated positions')[0]
        self.assertFalse(AUTHOR_PATTERN.search(narrative))
        self.assertIn('Fredrick White',text.split('id="natal-sources"')[1])
        self.assertIn('angles, houses and their interpretations are conditional',text)

    def test_natal_question_does_not_invoke_freeform_model(self):
        with patch('app.synthesize',side_effect=AssertionError('must not invoke model')):
            response=app.test_client().get('/api/agents/ask?question=Explain+my+natal+chart')
        self.assertEqual(response.status_code,200)
        self.assertIn('reader_edition',response.get_json()['grounded_natal'])


if __name__=='__main__':unittest.main()
