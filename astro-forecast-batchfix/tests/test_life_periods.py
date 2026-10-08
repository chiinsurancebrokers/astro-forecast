import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
import swisseph as swe
from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.natal_books import build_book_natal_report, citation
from astro.life_periods import transit_chapters, build_life_period_report
from astro.dasha import build_mahadashas, current_period


class LifePeriodTests(unittest.TestCase):
    def test_retrograde_reentry_is_retained_and_segments_are_contiguous(self):
        start = datetime(2026,1,1)
        jd0 = swe.julday(2026,1,1,12)
        def positions(jd,pid,flags):
            index = round(jd-jd0)
            longitude = [121,119,121,121][index]
            return ((longitude,0,1,0,0,0),flags)
        planets = {'Jupiter':{'sign':'Pisces','house':11},'Saturn':{'sign':'Cancer','house':3}}
        with patch('astro.life_periods.swe.calc_ut',side_effect=positions):
            chapters = transit_chapters(start,start+timedelta(days=3),'Taurus',planets)
        for name in ['Jupiter','Saturn']:
            parts = [c for c in chapters if c['planet']==name]
            self.assertEqual([c['house'] for c in parts],[4,3,4])
            self.assertTrue(parts[-1]['revisited'])
            self.assertEqual(parts[0]['end'],parts[1]['start'])
            self.assertEqual(parts[1]['end'],parts[2]['start'])

    def test_real_report_has_separate_dated_methods_and_no_house_guessing(self):
        init_ephemeris()
        chart = build_natal_chart(1975,2,8,11,20,2,37.9838,23.7275)
        natal = build_book_natal_report(chart,37.9838,23.7275)
        report = build_life_period_report(chart,natal['chart'],datetime(1975,2,8,9,20),datetime(2026,10,7),citation,years=1)
        self.assertEqual(report['end'],'2027-10-07')
        self.assertEqual(len(report['current_chapters']),2)
        self.assertTrue(all(c['start'] >= report['start'] and c['end'] <= report['end'] for c in report['chapters']))
        self.assertTrue(all(c['start'] < c['end'] for c in report['chapters']))
        self.assertTrue(all(c['from_house'] is not None for c in report['chapters'] if c['start']>report['start']))
        self.assertTrue(all(c['preparation'] for c in report['chapters']))
        self.assertTrue(report['vedic']['lifetime'])
        self.assertTrue(any(r['source_id']=='raphael_guide' and r['pdf_page']==126 for r in report['references']))
        self.assertIsNone(build_life_period_report(chart,None,datetime(1975,2,8),datetime(2026,10,7),citation))

    def test_major_period_boundary_selects_new_period(self):
        periods = build_mahadashas(datetime(2000,1,1),123.45)
        old = periods[0]
        new = periods[1]
        md,_ = current_period(periods,old['end'])
        self.assertEqual(md['lord'],new['lord'])
        self.assertNotEqual(md['lord'],old['lord'])
