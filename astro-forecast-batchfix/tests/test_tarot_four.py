import random
import unittest
from astro.tarot import draw_reading, deck
from astro.tarot_reading import TOPICS
from app import app


class FourCardTests(unittest.TestCase):
    def test_four_cards_positions_and_topic(self):
        r = draw_reading('Θα πάει καλά η σχέση μου;', 'four', 'el', True, random.Random(3), 'love')
        self.assertEqual([c['position_label'] for c in r['cards']], ['Παρελθόν', 'Παρόν', 'Μέλλον (τάση)', 'Απάντηση'])
        self.assertEqual(len({c['id'] for c in r['cards']}), 4)
        self.assertEqual(r['topic'], 'love')
        self.assertEqual(len(r['guide']), 4)
        self.assertIn('Θα πάει καλά η σχέση μου;', r['overall'])
        self.assertIn('τάση', r['overall'])
        self.assertIn('δεν λέει ναι ή όχι', r['overall'])
        self.assertNotIn('  ', r['overall'])

    def test_interpretation_depends_on_position_and_topic(self):
        card = {c['id']: c for c in deck()}['cups-02']

        class Fixed:
            def sample(self, cards, n): return [card] * n
            def getrandbits(self, n): return 0
        # same card in every slot would normally be impossible; used only to isolate wording
        texts = {(k, t): draw_reading('', 'four', 'en', False, Fixed(), t)['cards'][k]['interpretation']
                 for k in range(4) for t in ('love', 'money')}
        self.assertEqual(len(set(texts.values())), 8)
        self.assertIn('In love', texts[(0, 'love')])
        self.assertIn('With money', texts[(0, 'money')])

    def test_overall_is_a_story_from_the_draw(self):
        class Majors:
            def __init__(self, bit): self.bit = bit
            def sample(self, cards, n): return [c for c in cards if c['arcana'] == 'major'][:n]
            def getrandbits(self, n): return self.bit
        up = draw_reading('', 'four', 'en', True, Majors(0), 'general')['overall']
        rev = draw_reading('', 'four', 'en', True, Majors(1), 'general')['overall']
        self.assertIn('steady', up)
        self.assertIn('does not say yes or no', up)
        self.assertIn('points to', up)
        self.assertIn('ups and downs', rev)
        self.assertNotIn('Major Arcana cards', up)

    def test_all_topics_and_languages(self):
        for lang in ('el', 'en'):
            for topic in TOPICS:
                r = draw_reading('', 'four', lang, True, random.Random(1), topic)
                self.assertEqual(len(r['cards']), 4)
                self.assertNotIn('{', r['overall'] + ''.join(c['interpretation'] + c['reflection'] for c in r['cards']))

    def test_api_validation(self):
        client = app.test_client()
        ok = client.post('/api/tarot/draw', json={'spread': 'four', 'topic': 'love', 'lang': 'en'})
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(len(ok.get_json()['cards']), 4)
        self.assertEqual(client.post('/api/tarot/draw', json={'spread': 'four', 'topic': 'health'}).status_code, 400)
        self.assertEqual(client.post('/api/tarot/draw', json={'spread': 'five'}).status_code, 400)


if __name__ == '__main__':
    unittest.main()


class WordingTests(unittest.TestCase):
    def test_tied_suits_not_called_dominant(self):
        ids = ('swords-08', 'pentacles-08', 'swords-10', 'pentacles-02')

        class Fixed:
            def sample(self, cards, n):
                lookup = {c['id']: c for c in cards}
                return [lookup[i] for i in ids][:n]
            def getrandbits(self, n): return 0
        r = draw_reading('', 'four', 'en', False, Fixed(), 'self')
        self.assertNotIn('dominate', r['overall'])  # no dominance claims remain

    def test_major_lens_once_and_no_repeated_position_name(self):
        class Majors:
            def sample(self, cards, n): return [c for c in cards if c['arcana'] == 'major'][:n]
            def getrandbits(self, n): return 0
        r = draw_reading('', 'four', 'en', True, Majors(), 'self')
        self.assertEqual(sum('As a Major Arcana' in c['interpretation'] for c in r['cards']), 1)
        self.assertIn('shaped you', r['cards'][0]['interpretation'])
