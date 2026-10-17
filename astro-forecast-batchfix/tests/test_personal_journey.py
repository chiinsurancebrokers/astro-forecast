import unittest
from datetime import datetime
from unittest.mock import patch
from astro.personal_journey import date_window,aspect_crossings,build_personal_journey
from astro.ephemeris import init_ephemeris,build_natal_chart
from app import app

BIRTH={'year':1975,'month':2,'day':8,'hour':11,'minute':20,'utc_offset':2,'latitude':37.9838,'longitude':23.7275}

class JourneyTests(unittest.TestCase):
    def test_calendar_precision_and_validation(self):
        start,end,p=date_window('2024-02')
        self.assertEqual((end-start).days,29)
        self.assertEqual(p,'month')
        for invalid in ['2023-02-29','2005-13','2005/11',None]:
            with self.assertRaises((ValueError,TypeError)):date_window(invalid)

    def test_wraparound_and_retrograde_crossings(self):
        def calc(jd,pid,flags):
            # Both transit planets use the same mocked daily longitude.
            day=int(jd-2451545.0)
            lon=[359,1,359,1][day]
            return ([lon,0,1,1,0,0],0)
        with patch('astro.personal_journey.swe.julday',side_effect=lambda y,m,d,h:2451545.0+d-1),patch('astro.personal_journey.swe.calc_ut',side_effect=calc):
            contacts=aspect_crossings(datetime(2000,1,2),datetime(2000,1,5),{'Sun':0})
        self.assertEqual(len(contacts),6)
        self.assertTrue(all(c['aspect']=='conjunction' for c in contacts))
        self.assertEqual({c['date'] for c in contacts},{'2000-01-02','2000-01-03','2000-01-04'})

    def test_real_history_keeps_all_phases_and_future_separate(self):
        init_ephemeris();chart=build_natal_chart(1975,2,8,11,20,2,37.9838,23.7275)
        result=build_personal_journey(chart,37.9838,23.7275,{'events':[{'date':'2005-11','description':'Fictional change at home.'},{'date':'2009','end_date':'2022','description':'A long fictional period.'}],'responses':'I practised a skill.','goals':'Develop a contribution.'},datetime(2026,10,8))
        self.assertEqual(result['events'][0]['precision'],'month')
        self.assertIn('home and foundations',result['events'][0]['context_summary'])
        self.assertGreater(len(result['events'][1]['chapters']),10)
        self.assertEqual(result['notes']['goals'],'Develop a contribution.')
        self.assertTrue(all(c['date']>=result['life_report']['start'] for c in result['future_contacts']))
        self.assertIn('no',result['privacy'].lower())

    def test_post_validation_and_no_store(self):
        client=app.test_client()
        self.assertEqual(client.post('/api/agents/personal-journey',json={}).status_code,400)
        bad={**BIRTH,'latitude':float('nan')}
        payload={'birth':bad,'events':[{'date':'2005','description':'A fictional event.'}],'responses':'Learning.','goals':'A useful skill.'}
        self.assertEqual(client.post('/api/agents/personal-journey',json=payload).status_code,400)
        payload['birth']=BIRTH
        response=client.post('/api/agents/personal-journey',json=payload)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        payload['events'][0]['date']='not a date'
        self.assertEqual(client.post('/api/agents/personal-journey',json=payload).status_code,400)

if __name__=='__main__':unittest.main()
