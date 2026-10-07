import unittest
from astro.additional_books import additional_natal_sections, esoteric_sections, MERCURY
from astro.book_corpus import SOURCES, ENTRIES

def cite(source,pdf,printed,chapter):
    return {'source_id':source,'pdf_page':pdf,'printed_page':printed,'chapter':chapter}

class AdditionalBooksTests(unittest.TestCase):
    def test_exact_mercury_matching_and_locators(self):
        for sign,(_,page,printed) in MERCURY.items():
            section=additional_natal_sections({'Mercury':{'sign':sign}},cite)[0]
            self.assertEqual(section['citations'][0]['pdf_page'],page)
            self.assertEqual(section['citations'][0]['printed_page'],printed)
            self.assertIn(sign,section['paragraphs'][0])
        sections=additional_natal_sections({'Mercury':{'sign':'Aries'}},cite)
        self.assertEqual(len(sections),1)
        self.assertEqual(sections[0]['citations'][0]['source_id'],'bart_success')

    def test_esoteric_method_and_catalog_provenance(self):
        section=esoteric_sections({'Saturn':{'sign':'Cancer','house':3}},cite)[0]
        self.assertEqual(section['citations'][0]['system'],'ESOTERIC_HISTORICAL')
        self.assertIn('not a sign-specific',section['paragraphs'][1])
        for entry in ENTRIES:
            self.assertEqual(entry['system'],SOURCES[entry['source']]['system'])
        self.assertEqual(len({e['id'] for e in ENTRIES}),len(ENTRIES))

if __name__=='__main__': unittest.main()
