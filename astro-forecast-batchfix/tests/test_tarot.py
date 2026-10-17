import unittest
from astro.tarot import deck, draw_reading
from app import app


class FixedDraw:
    def sample(self,cards,count):
        lookup={c['id']:c for c in cards}
        return [lookup[key] for key in ('pentacles-07','wands-14','major-11')][:count]
    def getrandbits(self,_):
        return 1


class TarotTests(unittest.TestCase):
    def test_complete_deck_unique_ids_and_bilingual_content(self):
        cards=deck()
        self.assertEqual(len(cards),78)
        self.assertEqual(len({c['id'] for c in cards}),78)
        self.assertEqual(sum(c['arcana']=='major' for c in cards),22)
        for card in cards:
            for key in ('name_en','name_el','upright_en','upright_el','reversed_en','reversed_el'):
                self.assertTrue(card[key],(card['id'],key))

    def test_reading_has_distinct_cards_and_valid_orientations(self):
        reading=draw_reading()
        self.assertEqual(len({c['id'] for c in reading['cards']}),3)
        self.assertTrue(all(c['orientation'] in ('upright','reversed') for c in reading['cards']))
        self.assertEqual([c['position'] for c in reading['cards']],[0,1,2])

    def test_known_spread_preserves_order_and_no_reversals_option(self):
        reading=draw_reading(reversals=False,rng=FixedDraw())
        self.assertEqual([c['name'] for c in reading['cards']],
                         ['Επτά των Πεντάκτινων','Βασιλιάς των Ράβδων','Η Δικαιοσύνη'])
        self.assertTrue(all(c['orientation']=='upright' for c in reading['cards']))
        self.assertIn('υπομονετική προσπάθεια',reading['cards'][0]['interpretation'])
        self.assertIn('όραμα',reading['cards'][1]['interpretation'])

    def test_reverse_single_card_and_english(self):
        reading=draw_reading(spread='one',lang='en',rng=FixedDraw())
        self.assertEqual(len(reading['cards']),1)
        self.assertEqual(reading['cards'][0]['orientation'],'reversed')
        self.assertEqual(reading['cards'][0]['position_label'],'Focus for reflection')
        self.assertIn('reviewing',reading['cards'][0]['interpretation'])

    def test_post_only_and_question_is_not_in_url(self):
        client=app.test_client()
        response=client.post('/api/tarot/draw',json={'question':'  A private reflection  ','lang':'en'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertEqual(response.get_json()['question'],'A private reflection')
        self.assertEqual(client.get('/api/tarot/draw').status_code,405)

    def test_bad_inputs_are_rejected(self):
        client=app.test_client()
        for body in ([],None,{'question':[]},{'question':'a'*501},{'lang':'xx'},
                     {'spread':'horseshoe'},{'reversals':'false'},{'lang':[]}):
            response=client.post('/api/tarot/draw',json=body)
            self.assertEqual(response.status_code,400,body)
        self.assertEqual(client.post('/api/tarot/draw',data='x'*4097,
                                    content_type='application/json').status_code,413)

    def test_localized_pages_and_navigation(self):
        client=app.test_client()
        self.assertIn('Μια ερώτηση'.encode(),client.get('/tarot').data)
        self.assertIn(b'One question.',client.get('/tarot?lang=en').data)
        self.assertIn(b'/tarot',client.get('/platform').data)
        self.assertEqual(client.get('/static/tarot.js').status_code,200)


if __name__=='__main__':unittest.main()
